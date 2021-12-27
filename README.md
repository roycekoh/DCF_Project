# Automated DCF
A DCF or Discounted Cashflow Analysis is a valuation method that attempts to derive the intrinsic value of a company or estimate the value of an investment based on projections of its future cash flows. What sets a DCF apart from other valuation methods (Comps, Precedent) is that it can take into account qualitative factors and assumptions on how the business will perform in the future that can be variably weighted in order to derive this intrinsic value. This program attempts to leverage a number of ML models (GARCH Model, Decision Trees) in order to accurately weight these assumptions.

# Steps towards building a DCF
1. Forecast the future cash flows (3-5 years) of a company to find the unlevered free cash flow (EBIT - CAPEx + Dep & Amo - Non-Cash Capital)
2. Calculate the terminal value of a firm using the exit multiple approach, assuming the business is continuously sold by EV/EBITDA
3. Find the weighted average cost of capital (WACC) and use as the discount rate to discount the forecast period back to present value
4. Using this enterprise value, we derive the equity value by subtracting debt and adding cash

# ML Model Integration
This program leverages both decision trees and the garch model as its primary ML models. It will take historical financial data from Yahoo's API to perform the steps outlined above and use both precedent cash flows and comparable company's financials to build out the assumptions for the analysis. The GARCH model is a statistical model that leverage macroeconomic data to estimate the volatility of returns for an investment to determine pricing, specifically taking into account volatility in the market. It  estimates an autoregressive model, predicting future behavior based on prior financial information to determine if there is a significant correlation across a period of time. It will then calculate serial correlations or similarities between a model and a 'lagged' version of itself which is especially useful when using previous financial information to project future cash flows.
