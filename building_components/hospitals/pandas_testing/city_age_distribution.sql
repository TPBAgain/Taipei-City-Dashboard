select x_axis,y_axis,round(sum(data)/1000) data
from(select 區域別 as x_axis,'0_14歲人口數' as y_axis,percent24 as data
from 
public.city_age_distribution_taipei 
where 區域別 != '總計' and 年份=(select max(年份)
from 
public.city_age_distribution_taipei)
union all
select 區域別 as x_axis,'15_64歲人口數' as y_axis,percent26 as data
from 
public.city_age_distribution_taipei 
where 區域別 != '總計' and 年份=(select max(年份)
from 
public.city_age_distribution_taipei)
union all
select 區域別 as x_axis,'65歲以上人口數' as y_axis,percent28 as data
from 
public.city_age_distribution_taipei 
where 區域別 != '總計' and 年份=(select max(年份)
from 
public.city_age_distribution_taipei)
)d
group by x_axis,y_axis
