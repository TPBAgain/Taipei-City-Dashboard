package controllers

import (
	"TaipeiCityDashboardBE/app/models"
	"github.com/gin-gonic/gin"
	"net/http"
	"strconv"
)

func GetQuery(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": err.Error()})
	}
	city := c.Query("city")

	queryType, queryString, err := models.GetComponentChartDataQuery(id, city)
	c.JSON(http.StatusOK, gin.H{"queryType": queryType, "queryString": queryString})
}

func DoCustomQuerr