package controllers

import (
	"TaipeiCityDashboardBE/app/initial"
	"TaipeiCityDashboardBE/global"
	"TaipeiCityDashboardBE/logs"
	"bytes"
	"github.com/gin-gonic/gin"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func UploadSQLFileHandler(c *gin.Context) {
	file, err := c.FormFile("sql_file")
	if err != nil {
		logs.Error(err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "File upload failed", "details": err.Error()})
		return
	}

	tempDir := "/tmp/uploads"
	os.MkdirAll(tempDir, os.ModePerm)
	dst := filepath.Join(tempDir, filepath.Base(file.Filename))
	if err := c.SaveUploadedFile(file, dst); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not save file", "details": err.Error()})
		return
	}

	// Read file contents
	content, err := os.ReadFile(dst)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read SQL file", "details": err.Error()})
		return
	}

	lines := bytes.SplitN(content, []byte("\n"), 2)
	if len(lines) < 2 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "SQL file must have at least two lines (comment + SQL body)"})
		return
	}

	// Parse first line
	firstLine := string(bytes.TrimSpace(lines[0]))
	var dbTarget string
	if strings.HasPrefix(firstLine, "-- db:") {
		dbTarget = strings.TrimSpace(strings.TrimPrefix(firstLine, "-- db:"))
	} else {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing DB comment (e.g. `-- db: dashboard`)"})
		return
	}
	logs.Info(dbTarget)
	if dbTarget == "data" {
		err = initial.ExecuteSQLFile(global.PostgresDashboard, dst)
		if err != nil {
			logs.FError("error executing SQL file: %s", err)
			c.JSON(http.StatusBadRequest, gin.H{"error": "Error executing SQL file", "details": err.Error()})

		}

	}
	if dbTarget == "manager" {
		err = initial.ExecuteSQLFile(global.PostgresManager, dst)
		if err != nil {
			logs.FError("error executing SQL file: %s", err)
			c.JSON(http.StatusBadRequest, gin.H{"error": "Error executing SQL file", "details": err.Error()})
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "SQL executed successfully on " + dbTarget})
}
