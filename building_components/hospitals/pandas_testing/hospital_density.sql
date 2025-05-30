SELECT
  t.x_axis,
  t.y_axis   AS name,
  t.data
FROM (
  SELECT
    "行政區名稱"   AS x_axis,
    '診所'        AS y_axis,
    "診所"        AS data
  FROM public.hospital_density

  UNION ALL
  SELECT
    "行政區名稱",
    '地方醫院',
    "地方醫院"
  FROM public.hospital_density

  UNION ALL
  SELECT
    "行政區名稱",
    '區域醫院',
    "區域醫院"
  FROM public.hospital_density

  UNION ALL
  SELECT
    "行政區名稱",
    '醫學中心',
    "醫學中心"
  FROM public.hospital_density
) AS t
ORDER BY
  ARRAY_POSITION(
    ARRAY[
      '北投區','士林區','內湖區','南港區','松山區','信義區','中山區','大同區','中正區','萬華區',
      '大安區','文山區','新莊區','淡水區','汐止區','板橋區','三重區','樹林區','土城區','蘆洲區',
      '中和區','永和區','新店區','鶯歌區','三峽區','瑞芳區','五股區','泰山區','林口區','深坑區',
      '石碇區','坪林區','三芝區','石門區','八里區','平溪區','雙溪區','貢寮區','金山區','萬里區',
      '烏來區'
    ]::text[],
    t.x_axis
  ),
  ARRAY_POSITION(
    ARRAY['診所','地區醫院','區域醫院','醫學中心']::text[],
    t.y_axis
  );