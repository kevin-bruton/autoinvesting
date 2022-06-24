import { differenceInDays } from '../node_modules/date-fns/esm/index.js'
import getSortinoRatio from './sortino.js'
import { dec2 } from './index.js'

export {
  getMetrics
}
/**
 * Get metrics on trades performed
 * @param {Number} deposit - Initial capital deposited
 * @param {string} startDateStr - Start date of trading period (format: YYYY-MM-DD)
 * @param {string} endDateStr - End date of trading period (format: YYYY-MM-DD)
 * @param {Number[]} balances - Array of balance amounts at the end of each trade
 * @param {Number[]} profit - Array of profit amounts as a result of each trade
 * @returns {{ annnualPctRet: Number, maxDD: Number, maxPctDD: Number, annPctRetVsDdPct: Number }}
 */
function getMetrics (deposit, startDateStr, endDateStr, balances, profit) {
  const totalPctRet = dec2((balances[balances.length - 1] - deposit) / deposit * 100)
  const grossProfit = profit.reduce((gp, p) => p > 0 ? gp + p : gp, 0)
  const grossLoss = profit.reduce((gl, p) => p < 0 ? gl - p : gl, 0)
  const profitFactor = dec2(grossProfit / grossLoss)
  const numBacktestDays = differenceInDays(new Date(endDateStr), new Date(startDateStr))
  const annualPctRet = dec2(totalPctRet / (numBacktestDays / 365))
  const { maxDD } = balances
    .reduce(({ lastHigh, curDD, maxDD }, bal) => {
      if (bal < lastHigh) {
        curDD = lastHigh - bal
      } else if (bal > lastHigh) {
        lastHigh = bal
        curDD = 0
      }
      if (curDD > maxDD)
        maxDD = curDD
      return { lastHigh, curDD, maxDD }
    }, { lastHigh: deposit, curDD: 0, maxDD: 0 })
  const maxPctDD = dec2(maxDD / deposit * 100)
  const annPctRetVsDdPct = dec2(annualPctRet / maxPctDD)
  const sortino = getSortinoRatio(profit)
  return { annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, sortino, profitFactor }
}
