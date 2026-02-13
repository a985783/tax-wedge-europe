# Identification Strategy Design

## 1. Core Identification Strategy
**Methodology**: Stacked Event Study (Difference-in-Differences)
**Objective**: Estimate the dynamic pass-through elasticity of indirect tax shocks to consumer prices.

### The "Tax Wedge" Instrument
We exploit the mechanical identity between HICP and HICP-CT to isolate exogenous tax shocks:
$$ \Delta Wedge_{c,k,t} \approx \Delta \tau_{c,k,t} $$
*   **Threshold**: A "Tax Event" is defined when $|\Delta Wedge_{c,k,t}| \ge 1.0\%$.
*   **Granularity**: Country ($c$) $\times$ Product ($k$) $\times$ Month ($t$).

## 2. Econometric Specification
We estimate the following Stacked Event Study equation:

$$ \ln P_{c,k,t} - \ln P_{c,k,t^*_e-1} = \sum_{\tau=-12}^{12} \beta_\tau \cdot D_{e,t}^\tau \cdot \text{Size}_{e} + \mu_{c,k,e} + \lambda_{t,e} + \varepsilon_{c,k,t} $$

### Key Components
*   **Outcome**: Cumulative log price change relative to $t=-1$.
*   **Treatment**: $D_{e,t}^\tau$ is a dummy equal to 1 if observation is $\tau$ months away from event $e$.
*   **Scaling**: $\text{Size}_e$ is the continuous size of the tax shock (e.g., +0.05 for a 5% VAT hike).
*   **Sample Window**: $\tau \in [-12, +12]$ months.
*   **Fixed Effects**:
    *   $\mu_{c,k,e}$: Unit FE (absorbs time-invariant levels per stack).
    *   $\lambda_{t,e}$: Time FE (absorbs common shocks/seasonality per stack).

## 3. Control Group Definition
In the stacked design, the control group consists of:
1.  **Clean Controls**: Country-sector pairs that do *not* experience a tax shock $> 1\%$ within the event window ($\pm 12$ months).
2.  **Not-yet-treated**: Units that will be treated later (outside the current window).

**"Clean Window" Restriction**:
To ensure validity, any treated unit with *another* confounding shock $>1\%$ within $\pm 3$ months is dropped from the estimation.

## 4. Hypothesis Testing
*   **H0 (Full Pass-through)**: $\beta_{\tau \ge 0} = 1$
*   **H1 (Incomplete Pass-through)**: $\beta_{\tau \ge 0} < 1$
*   **H2 (Asymmetry)**: $\beta_{\tau}^{Hike} \neq \beta_{\tau}^{Cut}$
