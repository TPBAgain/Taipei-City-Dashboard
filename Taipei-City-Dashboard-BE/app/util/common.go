// Package util stores the utility functions for the application (functions that only handle internal logic)
/*
Developed By Taipei Urban Intelligence Center 2023-2024

// Lead Developer:  Igor Ho (Full Stack Engineer)
// Systems & Auth: Ann Shih (Systems Engineer)
// Data Pipelines:  Iima Yu (Data Scientist)
// Design and UX: Roy Lin (Prev. Consultant), Chu Chen (Researcher)
// Testing: Jack Huang (Data Scientist), Ian Huang (Data Analysis Intern)
*/
package util

import (
	"crypto/sha256"
	"errors"
	"fmt"
	"reflect"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// HashString takes a string as input, hashes it using SHA-256, and returns the hexadecimal representation of the hash.
func HashString(s string) string {
	h := sha256.New()
	h.Write([]byte(s))
	return fmt.Sprintf("%x", h.Sum(nil))
}

// MergeAndRemoveDuplicates merges multiple integer slices and removes duplicates.
func MergeAndRemoveDuplicates(slices ...[]int) []int {
	merged := make(map[int]struct{})

	// Merge two slices and remove duplicates
	for _, slice := range slices {
		for _, item := range slice {
			merged[item] = struct{}{}
		}
	}

	// Convert to slice
	result := make([]int, 0, len(merged))
	for item := range merged {
		result = append(result, item)
	}

	return result
}

// GetTime is a utility function to get the time from the header and set default values.
func GetTime(c *gin.Context) (string, string, error) {
	timefrom := c.Query("timefrom")
	timeto := c.Query("timeto")

	layout := "2006-01-02T15:04:05+08:00" // 定義時間格式

	// timeFrom defaults to 1990-01-01 (essentially, all data)
	if timefrom == "" {
		timefrom = time.Date(1990, 1, 1, 0, 0, 0, 0, time.FixedZone("UTC+8", 8*60*60)).Format(layout)
	} else {
		// 檢查 timefrom 格式
		if _, err := time.Parse(layout, timefrom); err != nil {
			return "", "", errors.New("timefrom 格式無效")
		}
	}
	// timeTo defaults to current time
	if timeto == "" {
		timeto = time.Now().Format(layout)
	} else {
		// 檢查 timeto 格式
		if _, err := time.Parse(layout, timeto); err != nil {
			return "", "", errors.New("timeto 格式無效")
		}
	}

	return timefrom, timeto, nil
}

func formatStringArray(arr []string) string {
	quoted := make([]string, len(arr))
	for i, v := range arr {
		quoted[i] = fmt.Sprintf("\"%s\"", strings.ReplaceAll(v, "\"", "\\\""))
	}
	return fmt.Sprintf("'{%s}'", strings.Join(quoted, ","))
}

func formatIntArray(arr []int) string {
	parts := make([]string, len(arr))
	for i, v := range arr {
		parts[i] = fmt.Sprintf("%d", v)
	}
	return fmt.Sprintf("'{%s}'", strings.Join(parts, ","))
}

func GenerateInsertSQLFromStruct(table string, item interface{}) string {
	v := reflect.ValueOf(item)
	t := reflect.TypeOf(item)

	if v.Kind() == reflect.Ptr {
		v = v.Elem()
		t = t.Elem()
	}

	columns := []string{}
	values := []string{}

	for i := 0; i < v.NumField(); i++ {
		field := v.Field(i)
		fieldType := t.Field(i)

		// Get column name from `gorm:"column:xxx"`
		col := fieldType.Tag.Get("gorm")
		if strings.Contains(col, "column:") {
			col = strings.Split(strings.Split(col, "column:")[1], ";")[0]
		}
		if col == "" {
			col = fieldType.Name
		}
		columns = append(columns, col)

		// Format values
		if !field.IsValid() || (field.Kind() == reflect.Ptr && field.IsNil()) {
			values = append(values, "NULL")
			continue
		}

		switch field.Kind() {
		case reflect.String:
			values = append(values, fmt.Sprintf("'%s'", strings.ReplaceAll(field.String(), "'", "''")))
		case reflect.Ptr:
			deref := field.Elem()
			if deref.Kind() == reflect.String {
				values = append(values, fmt.Sprintf("'%s'", strings.ReplaceAll(deref.String(), "'", "''")))
			} else {
				values = append(values, "NULL")
			}
		case reflect.Int, reflect.Int64:
			values = append(values, fmt.Sprintf("%d", field.Int()))
		case reflect.Slice:
			if field.Type().Elem().Kind() == reflect.Uint8 {
				// []byte → assume it's JSON
				values = append(values, fmt.Sprintf("'%s'", strings.ReplaceAll(string(field.Bytes()), "'", "''")))
			} else {
				values = append(values, "NULL")
			}
		case reflect.Struct:
			if field.Type().String() == "time.Time" {
				values = append(values, fmt.Sprintf("'%s'", field.Interface().(time.Time).Format("2006-01-02 15:04:05")))
			} else {
				values = append(values, "NULL")
			}
		default:
			values = append(values, "NULL")
		}
	}

	return fmt.Sprintf("INSERT INTO %s (%s) VALUES (%s);",
		table,
		strings.Join(columns, ", "),
		strings.Join(values, ", "),
	)
}
