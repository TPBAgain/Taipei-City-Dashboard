package util

import (
	"bytes"
	"fmt"
	"reflect"
	"strconv"
	"strings"
	"time"
)

// -------- core public API ---------------------------------------------------

func GenerateInsertSQLFromStruct(table string, item any) string {
	v := reflect.ValueOf(item)
	t := reflect.TypeOf(item)
	if v.Kind() == reflect.Ptr {
		v, t = v.Elem(), t.Elem()
	}

	var cols, vals []string

	for i := 0; i < v.NumField(); i++ {
		ft := t.Field(i)
		tag := ft.Tag.Get("gorm")

		// 1. skip ignored / auto fields
		if tag == "-" ||
			strings.Contains(tag, "autoCreateTime") ||
			strings.Contains(tag, "autoUpdateTime") ||
			strings.Contains(tag, "primaryKey") {
			continue
		}

		// 2. column name
		col := parseColumnName(ft.Name, tag)
		cols = append(cols, pqIdent(col))

		// 3. value literal
		vals = append(vals, pgLiteral(v.Field(i)))
	}

	return fmt.Sprintf(
		"INSERT INTO %s (%s) VALUES (%s);",
		pqIdent(table),
		strings.Join(cols, ", "),
		strings.Join(vals, ", "),
	)
}

// -------- helpers -----------------------------------------------------------

// parseColumnName extracts column:foo from the gorm tag or falls back to struct name
func parseColumnName(fallback, tag string) string {
	if idx := strings.Index(tag, "column:"); idx >= 0 {
		tag = tag[idx+len("column:"):]
		if semi := strings.IndexByte(tag, ';'); semi >= 0 {
			return tag[:semi]
		}
		return tag
	}
	return fallback
}

// pqIdent adds double quotes if the identifier is mixed-case or reserved
func pqIdent(id string) string {
	if strings.ContainsAny(id, `" `) || strings.ToLower(id) != id {
		return `"` + strings.ReplaceAll(id, `"`, `""`) + `"`
	}
	return id
}

// pgLiteral converts any Go value into a safe Postgres literal
func pgLiteral(v reflect.Value) string {
	if !v.IsValid() || (v.Kind() == reflect.Ptr && v.IsNil()) {
		return "NULL"
	}

	// de-reference pointers
	if v.Kind() == reflect.Ptr {
		v = v.Elem()
	}

	switch v.Kind() {
	case reflect.String:
		if v.String() == "" {
			return "NULL"
		}
		return pgQuote(v.String())
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return strconv.FormatInt(v.Int(), 10)
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		return strconv.FormatUint(v.Uint(), 10)
	case reflect.Float32, reflect.Float64:
		return strconv.FormatFloat(v.Float(), 'f', -1, 64)
	case reflect.Bool:
		if v.Bool() {
			return "TRUE"
		}
		return "FALSE"
	case reflect.Slice: // treat []byte as JSON/text
		if v.Type().Elem().Kind() == reflect.Uint8 {
			ret := pgQuote(string(v.Bytes()))
			if ret == "" {
				return "{}"
			}
			return ret
		}
	case reflect.Struct:
		if v.Type().String() == "time.Time" {
			return pgQuote(v.Interface().(time.Time).Format("2006-01-02 15:04:05"))
		}
	}
	// fallback
	return "NULL"
}

// pgQuote chooses single quotes for short 1-line strings
// and dollar-quotes for anything containing \n or ' or CR
func pgQuote(s string) string {
	// normalise CRLF
	s = strings.ReplaceAll(s, "\r\n", "\n")

	if !strings.ContainsAny(s, "\n'") {
		return "'" + strings.ReplaceAll(s, `'`, `''`) + "'"
	}

	// pick a delimiter that doesn't appear in the string
	delim := "$$"
	for strings.Contains(s, delim) {
		delim = "$q$"
	}
	var buf bytes.Buffer
	buf.WriteString(delim)
	buf.WriteString(s)
	buf.WriteString(delim)
	return buf.String()
}
