FROM golang:1.23.0-alpine as builder
WORKDIR /go/src/app
COPY . .
# builder stage
RUN CGO_ENABLED=0 go build -o TaipeiCityDashboardBE -ldflags="-s -w"


FROM scratch
COPY --from=builder /go/src/app/TaipeiCityDashboardBE /app/
WORKDIR /app
ENTRYPOINT ["./TaipeiCityDashboardBE"]
