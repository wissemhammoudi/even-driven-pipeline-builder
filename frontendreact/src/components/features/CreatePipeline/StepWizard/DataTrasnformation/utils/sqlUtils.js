export const cleanSQLResponse = (sqlString) => {
  if (!sqlString) return ''
  
  let sqlStr = String(sqlString)
  
  sqlStr = sqlStr.replace(/^['"]{3,}/, '').replace(/['"]{3,}$/, '')
  sqlStr = sqlStr.replace(/^```sql\s*/i, '').replace(/\s*```$/i, '')
  sqlStr = sqlStr.replace(/^```\s*/i, '').replace(/\s*```$/i, '')
  
  sqlStr = sqlStr.trim()
  
  return sqlStr
}
