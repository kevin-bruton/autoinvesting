import { dec2 } from './index.js'

/**
 * @method getSortinoRatio
 * @summary Sortino ratio
 * @description Calculate a Sortino ratio - a measure of risk similar to Sharpe ratio based on downside deviation
 * 
 * @param  {array} returnValues asset/portfolio return values
 * @param  {number} riskFreeRate expected portfolio return (default 0)
 * @return {number}
 *
 * @example
 * const return_values = [2, 1, -1, 18, 8, -2, 1, -1]
 *
 * getSortinoRatio(return_values);
 * // 3.7527767497325675
 * 
 */

 export default function getSortinoRatio (returnValues, riskFreeRate = 3) {

	// 1)  Calculate the numerator of the 
	// Sortino ratio, the average period 
	// return minus the target return
	const avgReturn = returnValues.reduce( ( a, b ) => a + b, 0 ) / returnValues.length;

	const sortinoNumerator = avgReturn - riskFreeRate

	// 2) For each data point, calculate
	// the difference between that data
	// point and the risk free rate. For data
	// points above the risk free rate, set
	// the difference to 0%. The result of
	// this step is the underperformance
	// data set
	const underperformance = returnValues.map( p => Math.min( riskFreeRate, p - riskFreeRate ) )

	// 3) Calculate the square of each
	// value in the underperformance data
	// set 
	const underperformanceSquared = underperformance.map( p => Math.pow(p, 2) )

	// 4) Calculate the average of all
	// squared differences determined in
	// Step 3
	const underperformanceSquaredAverage = underperformanceSquared.reduce( ( a, b ) => a + b, 0 ) / underperformanceSquared.length

	// 5) Take the square root of the
	// average determined in Step 4. This
	// is the risk free rate downside deviation
	// used in the denominator of the
	// Sortino ratio
	const targetDownsideDeviation = Math.sqrt(underperformanceSquaredAverage)

	// 6) Calculate the Sortino ratio
	const sortinoRatio = sortinoNumerator / targetDownsideDeviation

	return dec2(sortinoRatio)
}
