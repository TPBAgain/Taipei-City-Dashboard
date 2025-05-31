package controllers

import (
	"TaipeiCityDashboardBE/app/models"
	"TaipeiCityDashboardBE/app/util"
	"TaipeiCityDashboardBE/global"
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

	// Safely stream output
	if _, err := io.Copy(c.Writer, stdout); err != nil {
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

func DumpComponentHandler(c *gin.Context) {
	index := c.Param("index")

	var insertSql []string

	// 1. Components (can be many)
	var components []Component
	if err := models.DBManager.Table("components").
		Where("index = ?", index).Find(&components).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch components", "details": err.Error()})
		return
	}
	for _, comp := range components {
		insertSql = append(insertSql, util.GenerateInsertSQLFromStruct("components", comp))
	}

	// 2. QueryCharts (can be many)
	var charts []QueryChart
	if err := models.DBManager.Table("query_charts").
		Where("index = ?", index).Find(&charts).Error; err == nil {
		for _, chart := range charts {
			insertSql = append(insertSql, util.GenerateInsertSQLFromStruct("query_charts", chart))
		}
	}

	// 3. ComponentMaps (optional, can be many)
	var maps []ComponentMap
	if err := models.DBManager.Table("component_maps").
		Where("index = ?", index).Find(&maps).Error; err == nil {
		for _, m := range maps {
			insertSql = append(insertSql, util.GenerateInsertSQLFromStruct("component_maps", m))
		}
	}

	// 4. Return as SQL text
	c.Data(http.StatusOK, "text/plain; charset=utf-8", []byte(strings.Join(insertSql, "\n\n")))
}
