package controllers

import (
	"TaipeiCityDashboardBE/global"
	"TaipeiCityDashboardBE/logs"
	"bufio"
	"bytes"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/lib/pq"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"
)

// GET api/v1/test/:index
// Returns the dump .sql file of the table named plain text

func DumpTableHandler(c *gin.Context) {
	table := c.Param("index")
	if table == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'table' query parameter"})
		return
	}

	cmd := exec.Command("pg_dump",
		"-h", global.PostgresDashboard.Host,
		"-p", global.PostgresDashboard.Port,
		"-U", global.PostgresDashboard.User,
		"-t", table,
		global.PostgresDashboard.DBName)
	cmd.Env = append(os.Environ(),
		"PGPASSWORD="+global.PostgresDashboard.Password,
	)

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get stdout", "details": err.Error()})
		return
	}

	if err := cmd.Start(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to start pg_dump", "details": err.Error()})
		return
	}

	c.Header("Content-Disposition", "inline; filename="+table+".sql")
	c.Header("Content-Type", "application/sql")
	c.Status(http.StatusOK)

	// Prepend the header string
	header := bytes.NewReader([]byte("-- db: data\n"))
	combinedReader := io.MultiReader(header, stdout)

	if _, err := io.Copy(c.Writer, combinedReader); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to stream dump", "details": err.Error()})
		return
	}

	_ = cmd.Wait()
}

type Component struct {
	ID    string `gorm:"column:id"`
	Index string `gorm:"column:index"`
	Name  string `gorm:"column:name"`
}
type QueryChart struct {
	Index          string         `gorm:"column:index"`
	HistoryConfig  []byte         `gorm:"column:history_config"` // JSON as []byte
	MapConfigIDs   pq.Int64Array  `gorm:"column:map_config_ids"` // Postgres integer[]
	MapFilter      []byte         `gorm:"column:map_filter"`     // JSON as []byte
	TimeFrom       string         `gorm:"column:time_from"`
	TimeTo         string         `gorm:"column:time_to"`
	UpdateFreq     int            `gorm:"column:update_freq"`
	UpdateFreqUnit string         `gorm:"column:update_freq_unit"`
	Source         string         `gorm:"column:source"`
	ShortDesc      string         `gorm:"column:short_desc"`
	LongDesc       string         `gorm:"column:long_desc"`
	UseCase        string         `gorm:"column:use_case"`
	Links          pq.StringArray `gorm:"column:links"`        // Postgres text[]
	Contributors   pq.StringArray `gorm:"column:contributors"` // Postgres text[]
	CreatedAt      time.Time      `gorm:"column:created_at"`
	UpdatedAt      time.Time      `gorm:"column:updated_at"`
	QueryType      string         `gorm:"column:query_type"`
	QueryChart     string         `gorm:"column:query_chart"`
	QueryHistory   string         `gorm:"column:query_history"`
	City           string         `gorm:"column:city"`
}
type ComponentMap struct {
	ID       int64   `gorm:"column:id"`
	Index    string  `gorm:"column:index"`
	Title    string  `gorm:"column:title"`
	Type     string  `gorm:"column:type"`
	Source   string  `gorm:"column:source"`
	Size     *string `gorm:"column:size"`  // nullable
	Icon     *string `gorm:"column:icon"`  // nullable
	Paint    []byte  `gorm:"column:paint"` // JSON
	Property []byte  `gorm:"column:property"`
}

// GET /api/v1/test/component/:index
// DumpComponentHandler dumps rows whose "index" matches the URL param
// using pg_dump rather than reflection/GORM marshalling.
func DumpComponentHandler(c *gin.Context) {
	index := c.Param("index") // e.g. "ebus_percent"

	dbCfg := global.PostgresManager // or fetch from viper/env

	host := dbCfg.Host // "localhost" or service name
	port := dbCfg.Port // "5432"
	user := dbCfg.User
	pass := dbCfg.Password
	name := dbCfg.DBName // "dashboard_manager"

	tables := []string{
		"components",
		"query_charts",
		"component_maps",
	}

	var sqlChunks []string
	sqlChunks = append(sqlChunks, "-- db: manager\n")

	for _, tbl := range tables {
		dump, err := pgDumpSingleTable(host, port, user, pass, name, tbl, index)
		if err != nil {
			// If one table is missing, skip it but log the error.
			logs.Warn("pg_dump %s failed: %v", tbl, err)
			continue
		}
		filtered := filterSQLLines(dump, index)
		if len(filtered) > 0 {
			sqlChunks = append(sqlChunks, strings.Join(filtered, "\n"))
		}
	}

	if len(sqlChunks) == 1 { // only header => nothing dumped
		c.JSON(http.StatusNotFound,
			gin.H{"error": "no rows found for index", "index": index})
		return
	}

	fileName := fmt.Sprintf("%s_dump.sql", index)
	c.Header("Content-Disposition",
		fmt.Sprintf(`attachment; filename="%s"`, fileName))
	c.Data(http.StatusOK, "application/sql",
		[]byte(strings.Join(sqlChunks, "\n\n")))
}

// pgDumpSingleTable executes pg_dump for exactly one table + where clause
func pgDumpSingleTable(host, port, user, pass, dbName, table, index string) (string, error) {
	args := []string{
		"-h", host,
		"-p", port,
		"-U", user,
		"--data-only",
		"--column-inserts",
		"-t", table,
		dbName,
	}
	cmd := exec.Command("pg_dump", args...)
	// Inject password so pg_dump won’t prompt
	cmd.Env = append(os.Environ(), fmt.Sprintf("PGPASSWORD=%s", pass))

	var out bytes.Buffer
	var errBuf bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &errBuf

	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("%w: %s", err, errBuf.String())
	}
	return out.String(), nil
}

func filterSQLLines(sqlDump string, target string) []string {
	var lines []string
	scanner := bufio.NewScanner(strings.NewReader(sqlDump))
	for scanner.Scan() {
		line := scanner.Text()
		// match exact ID or index. Could extend this to be more precise.
		if strings.Contains(line, target) {
			lines = append(lines, line, "\n")
		}
	}
	return lines
}
