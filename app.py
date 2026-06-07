import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="SIP Calculator",
    page_icon="💰",
    layout="wide"
)

st.title("💰 SIP & Investment Calculator")
st.markdown("Plan your wealth — SIP, lumpsum, "
            "goal planning and retirement calculator.")
st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 SIP Calculator",
    "💵 Lumpsum Calculator",
    "🎯 Goal Planner",
    "🏖️ Retirement Planner",
    "📊 Fund Comparison"
])

# Tab 1 — SIP
with tab1:
    st.markdown("### 📈 SIP Calculator")
    st.markdown("Systematic Investment Plan — "
                "invest a fixed amount every month.")

    col1, col2 = st.columns(2)

    with col1:
        monthly_sip = st.number_input(
            "Monthly SIP Amount (₹):",
            min_value=500,
            max_value=1000000,
            value=5000,
            step=500
        )
        annual_return = st.slider(
            "Expected Annual Return (%):",
            1.0, 30.0, 12.0, 0.5
        )
        years = st.slider(
            "Investment Duration (Years):",
            1, 40, 10, 1
        )
        step_up = st.slider(
            "Annual SIP Step-up (%):",
            0, 30, 0, 1,
            help="Increase SIP amount annually"
        )

    with col2:
        # Calculations
        months       = years * 12
        monthly_rate = annual_return / 100 / 12

        if step_up == 0:
            # Standard SIP formula
            future_value = monthly_sip * (
                ((1 + monthly_rate) ** months - 1)
                / monthly_rate
            ) * (1 + monthly_rate)
            total_invested = monthly_sip * months
        else:
            # Step-up SIP
            future_value   = 0
            total_invested = 0
            current_sip    = monthly_sip
            for year in range(years):
                for month in range(12):
                    remaining = months - \
                        (year * 12 + month)
                    future_value += current_sip * \
                        (1 + monthly_rate) ** remaining
                    total_invested += current_sip
                current_sip *= (1 + step_up / 100)

        wealth_gained = future_value - total_invested
        returns_pct   = (wealth_gained /
                         total_invested * 100)

        st.markdown("### 💎 Results")
        st.markdown(
            f"<h2 style='color:#2ecc71'>"
            f"₹{future_value/1e7:.2f} Crores"
            f"</h2>",
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Invested",
                  f"₹{total_invested/1e5:.1f}L")
        c2.metric("Wealth Gained",
                  f"₹{wealth_gained/1e5:.1f}L")
        c3.metric("Returns",
                  f"{returns_pct:.0f}%")

    # Growth chart
    months_list  = list(range(1, months + 1))
    invested_cum = []
    value_cum    = []
    curr_sip     = monthly_sip
    total_inv    = 0
    port_val     = 0

    for i, m in enumerate(months_list):
        if step_up > 0 and i > 0 and \
                i % 12 == 0:
            curr_sip *= (1 + step_up / 100)
        total_inv += curr_sip
        port_val   = port_val * \
            (1 + monthly_rate) + curr_sip
        invested_cum.append(total_inv)
        value_cum.append(port_val)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[m/12 for m in months_list],
        y=[v/1e5 for v in value_cum],
        fill='tozeroy',
        name='Portfolio Value',
        line=dict(color='#2ecc71', width=2),
        fillcolor='rgba(46,204,113,0.15)'
    ))
    fig.add_trace(go.Scatter(
        x=[m/12 for m in months_list],
        y=[v/1e5 for v in invested_cum],
        fill='tozeroy',
        name='Amount Invested',
        line=dict(color='#3498db', width=2),
        fillcolor='rgba(52,152,219,0.15)'
    ))
    fig.update_layout(
        title='SIP Growth Over Time',
        xaxis_title='Years',
        yaxis_title='Amount (₹ Lakhs)',
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig,
                    use_container_width=True)

    # Year-wise breakdown
    st.markdown("#### 📋 Year-wise Breakdown")
    yearly_data = []
    curr_sip_y  = monthly_sip
    running_inv = 0
    running_val = 0

    for year in range(1, years + 1):
        for month in range(12):
            running_inv += curr_sip_y
            running_val  = running_val * \
                (1 + monthly_rate) + curr_sip_y
        yearly_data.append({
            'Year':      year,
            'Invested':  f"₹{running_inv/1e5:.1f}L",
            'Value':     f"₹{running_val/1e5:.1f}L",
            'Gain':      f"₹{(running_val-running_inv)/1e5:.1f}L",
            'Growth %':  f"{(running_val-running_inv)/running_inv*100:.0f}%"
        })
        if step_up > 0:
            curr_sip_y *= (1 + step_up / 100)

    year_df = pd.DataFrame(yearly_data)
    st.dataframe(year_df,
                 use_container_width=True,
                 hide_index=True)

# Tab 2 — Lumpsum
with tab2:
    st.markdown("### 💵 Lumpsum Calculator")

    col1, col2 = st.columns(2)

    with col1:
        lumpsum_amt = st.number_input(
            "Lumpsum Amount (₹):",
            min_value=1000,
            max_value=100000000,
            value=100000,
            step=10000
        )
        ls_return = st.slider(
            "Expected Annual Return (%):",
            1.0, 30.0, 12.0, 0.5,
            key="ls_return"
        )
        ls_years = st.slider(
            "Investment Duration (Years):",
            1, 40, 10, 1,
            key="ls_years"
        )
        inflation = st.slider(
            "Inflation Rate (%):",
            2.0, 10.0, 6.0, 0.5
        )

    with col2:
        ls_future = lumpsum_amt * \
            (1 + ls_return/100) ** ls_years
        ls_real   = lumpsum_amt * \
            (1 + (ls_return - inflation)/100) \
            ** ls_years
        ls_gain   = ls_future - lumpsum_amt
        cagr      = ((ls_future/lumpsum_amt) **
                     (1/ls_years) - 1) * 100

        st.markdown("### 💎 Results")
        st.markdown(
            f"<h2 style='color:#f39c12'>"
            f"₹{ls_future/1e7:.3f} Crores"
            f"</h2>",
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)
        c1.metric("Nominal Value",
                  f"₹{ls_future/1e5:.1f}L")
        c2.metric("Real Value (inflation adj.)",
                  f"₹{ls_real/1e5:.1f}L")
        c3, c4 = st.columns(2)
        c3.metric("Total Gain",
                  f"₹{ls_gain/1e5:.1f}L")
        c4.metric("CAGR",
                  f"{cagr:.1f}%")

    # Rule of 72
    st.markdown("#### ⚡ Rule of 72")
    doubling_time = 72 / ls_return
    st.info(
        f"At {ls_return}% return, your money "
        f"doubles every **{doubling_time:.1f} years**. "
        f"₹{lumpsum_amt/1e5:.1f}L becomes "
        f"₹{lumpsum_amt*2/1e5:.1f}L in "
        f"{doubling_time:.1f} years.")

    # Growth comparison
    returns_list = [6, 8, 10, 12, 15, 18, 20]
    comp_data    = [{
        'Return %': r,
        'Value (₹L)': round(
            lumpsum_amt *
            (1 + r/100) ** ls_years / 1e5, 1),
        'Gain (₹L)': round(
            (lumpsum_amt *
             (1 + r/100) ** ls_years -
             lumpsum_amt) / 1e5, 1)
    } for r in returns_list]

    comp_df = pd.DataFrame(comp_data)
    fig2    = px.bar(
        comp_df,
        x='Return %',
        y='Value (₹L)',
        title=f'Final Value at Different Returns '
              f'({ls_years} years)',
        color='Value (₹L)',
        color_continuous_scale='Greens'
    )
    fig2.update_layout(
        height=350,
        template='plotly_white'
    )
    st.plotly_chart(fig2,
                    use_container_width=True)

# Tab 3 — Goal Planner
with tab3:
    st.markdown("### 🎯 Goal-Based Planner")
    st.markdown("How much SIP do you need "
                "to achieve your goal?")

    col1, col2 = st.columns(2)

    with col1:
        goal_name = st.selectbox(
            "Goal:",
            ["🏠 Buy a House",
             "🎓 Child's Education",
             "💒 Wedding",
             "✈️ International Travel",
             "🚗 Buy a Car",
             "🆓 Financial Freedom",
             "Custom Goal"]
        )

        goal_defaults = {
            "🏠 Buy a House":          (5000000, 15),
            "🎓 Child's Education":    (2000000, 18),
            "💒 Wedding":              (1500000, 5),
            "✈️ International Travel": (300000,  3),
            "🚗 Buy a Car":            (800000,  5),
            "🆓 Financial Freedom":    (10000000,20),
            "Custom Goal":             (1000000, 10)
        }

        default_amt, default_yrs = \
            goal_defaults.get(
                goal_name, (1000000, 10))

        goal_amount = st.number_input(
            "Target Amount (₹):",
            min_value=10000,
            max_value=500000000,
            value=default_amt,
            step=50000
        )
        goal_years = st.slider(
            "Years to achieve:",
            1, 40, default_yrs
        )
        goal_return = st.slider(
            "Expected Return (%):",
            6.0, 25.0, 12.0, 0.5,
            key="goal_return"
        )
        existing_corpus = st.number_input(
            "Existing savings (₹):",
            min_value=0,
            value=0,
            step=10000
        )

    with col2:
        goal_months = goal_years * 12
        goal_rate   = goal_return / 100 / 12

        # Future value of existing corpus
        corpus_fv = existing_corpus * \
            (1 + goal_return/100) ** goal_years

        # Remaining amount needed
        remaining = max(0,
                        goal_amount - corpus_fv)

        # Required SIP
        if remaining > 0 and goal_rate > 0:
            req_sip = remaining * goal_rate / (
                ((1 + goal_rate) **
                 goal_months - 1) *
                (1 + goal_rate)
            )
        else:
            req_sip = 0

        st.markdown("### 🎯 Required SIP")
        st.markdown(
            f"<h2 style='color:#9b59b6'>"
            f"₹{req_sip:,.0f}/month"
            f"</h2>",
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)
        c1.metric("Goal Amount",
                  f"₹{goal_amount/1e5:.1f}L")
        c2.metric("Corpus Contribution",
                  f"₹{corpus_fv/1e5:.1f}L")
        c3, c4 = st.columns(2)
        c3.metric("SIP Needed",
                  f"₹{req_sip:,.0f}/mo")
        c4.metric("Total to Invest",
                  f"₹{req_sip*goal_months/1e5:.1f}L")

        # Progress if you start now
        if req_sip > 0:
            affordability = min(
                req_sip / 50000 * 100, 100)
            st.progress(
                min(affordability/100, 1.0))
            st.caption(
                f"₹{req_sip:,.0f}/month — "
                f"start today!")

    # Goal timeline
    sip_val  = 0
    sip_data = []
    for m in range(1, goal_months + 1):
        sip_val = sip_val * \
            (1 + goal_rate) + req_sip + \
            existing_corpus * \
            (1 + goal_rate) ** (m/12) / \
            goal_months
        if m % 12 == 0:
            sip_data.append({
                'Year':  m // 12,
                'Value': sip_val
            })

    if sip_data:
        sip_df = pd.DataFrame(sip_data)
        fig3   = go.Figure()
        fig3.add_trace(go.Scatter(
            x=sip_df['Year'],
            y=sip_df['Value'] / 1e5,
            fill='tozeroy',
            name='Portfolio Value',
            line=dict(color='#9b59b6',
                      width=2),
            fillcolor='rgba(155,89,182,0.15)'
        ))
        fig3.add_hline(
            y=goal_amount/1e5,
            line_dash="dash",
            line_color="red",
            annotation_text=
                f"Goal: ₹{goal_amount/1e5:.0f}L"
        )
        fig3.update_layout(
            title=f'Path to {goal_name}',
            xaxis_title='Years',
            yaxis_title='Amount (₹ Lakhs)',
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(
            fig3,
            use_container_width=True)

# Tab 4 — Retirement
with tab4:
    st.markdown("### 🏖️ Retirement Planner")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 👤 Your Profile")
        current_age    = st.slider(
            "Current Age:", 18, 55, 22)
        retirement_age = st.slider(
            "Retirement Age:", 45, 70, 60)
        life_expectancy = st.slider(
            "Life Expectancy:", 70, 100, 85)
        current_salary = st.number_input(
            "Monthly Salary (₹):",
            min_value=0,
            value=30000,
            step=5000
        )

    with col2:
        st.markdown("#### 💰 Financial Details")
        monthly_expenses = st.number_input(
            "Monthly Expenses (₹):",
            min_value=0,
            value=20000,
            step=1000
        )
        existing_savings = st.number_input(
            "Existing Savings (₹):",
            min_value=0,
            value=50000,
            step=10000
        )
        ret_return = st.slider(
            "Pre-retirement Return (%):",
            8.0, 20.0, 12.0, 0.5
        )
        post_ret_return = st.slider(
            "Post-retirement Return (%):",
            4.0, 12.0, 7.0, 0.5
        )

    with col3:
        st.markdown("#### 📊 Assumptions")
        inflation_ret = st.slider(
            "Inflation Rate (%):",
            3.0, 10.0, 6.0, 0.5,
            key="ret_inflation"
        )
        replace_ratio = st.slider(
            "Income Replacement (%):",
            50, 100, 70,
            help="% of current income needed "
                 "in retirement"
        )

        years_to_retire = \
            retirement_age - current_age
        years_in_retire = \
            life_expectancy - retirement_age

        # Monthly retirement need
        monthly_ret_need = monthly_expenses * \
            (replace_ratio / 100) * \
            ((1 + inflation_ret/100) **
             years_to_retire)

        # Corpus needed at retirement
        real_ret_rate = (
            (1 + post_ret_return/100) /
            (1 + inflation_ret/100) - 1
        )
        if real_ret_rate > 0:
            corpus_needed = monthly_ret_need * \
                12 / real_ret_rate * \
                (1 - (1 + real_ret_rate) **
                 (-years_in_retire))
        else:
            corpus_needed = monthly_ret_need * \
                12 * years_in_retire

        # Existing savings future value
        savings_fv = existing_savings * \
            (1 + ret_return/100) ** \
            years_to_retire

        # SIP needed
        remaining_corpus = max(
            0, corpus_needed - savings_fv)
        ret_months = years_to_retire * 12
        ret_rate   = ret_return / 100 / 12

        if remaining_corpus > 0 and \
                ret_rate > 0:
            ret_sip = remaining_corpus * \
                ret_rate / (
                    ((1 + ret_rate) **
                     ret_months - 1) *
                    (1 + ret_rate)
                )
        else:
            ret_sip = 0

        st.metric("Corpus Needed",
                  f"₹{corpus_needed/1e7:.2f}Cr")
        st.metric("Monthly SIP Required",
                  f"₹{ret_sip:,.0f}")
        st.metric("Years to Retire",
                  years_to_retire)
        st.metric("Retirement Years",
                  years_in_retire)

    # Retirement summary
    st.markdown("---")
    st.markdown("### 📊 Retirement Summary")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Retire at Age",
              retirement_age)
    r2.metric("Monthly Need (today)",
              f"₹{monthly_expenses:,}")
    r3.metric("Monthly Need (at retire)",
              f"₹{monthly_ret_need:,.0f}")
    r4.metric("Total Corpus Needed",
              f"₹{corpus_needed/1e7:.2f} Cr")

    # Retirement corpus build-up chart
    corpus_data = []
    running_val = existing_savings
    for year in range(1, years_to_retire + 1):
        for month in range(12):
            running_val = running_val * \
                (1 + ret_rate) + ret_sip
        corpus_data.append({
            'Age':    current_age + year,
            'Corpus': running_val
        })

    corpus_df = pd.DataFrame(corpus_data)
    fig4      = go.Figure()
    fig4.add_trace(go.Area(
        x=corpus_df['Age'],
        y=corpus_df['Corpus'] / 1e7,
        name='Corpus Built',
        line=dict(color='#27ae60', width=2),
        fillcolor='rgba(39,174,96,0.2)'
    ))
    fig4.add_hline(
        y=corpus_needed/1e7,
        line_dash="dash",
        line_color="red",
        annotation_text=
            f"Target: ₹{corpus_needed/1e7:.1f}Cr"
    )
    fig4.update_layout(
        title='Retirement Corpus Build-up',
        xaxis_title='Age',
        yaxis_title='Corpus (₹ Crores)',
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig4,
                    use_container_width=True)

# Tab 5 — Fund Comparison
with tab5:
    st.markdown("### 📊 Mutual Fund Categories")
    st.markdown("Compare expected returns "
                "across fund types.")

    fund_data = {
        'Fund Type': [
            'Large Cap', 'Mid Cap',
            'Small Cap', 'Flexi Cap',
            'Index Fund (Nifty 50)',
            'ELSS (Tax Saving)',
            'Debt Fund', 'Liquid Fund',
            'Hybrid Balanced',
            'International Fund'
        ],
        'Avg 3Y Return (%)': [
            12, 18, 22, 15, 13,
            14, 7, 6, 11, 10
        ],
        'Avg 5Y Return (%)': [
            14, 20, 25, 16, 14,
            15, 8, 6.5, 12, 11
        ],
        'Risk Level': [
            'Low-Medium', 'High',
            'Very High', 'Medium-High',
            'Low-Medium', 'High',
            'Low', 'Very Low',
            'Medium', 'Medium-High'
        ],
        'Min SIP (₹)': [
            500, 500, 500, 500, 100,
            500, 500, 1000, 500, 500
        ]
    }

    fund_df = pd.DataFrame(fund_data)

    col1, col2 = st.columns(2)

    with col1:
        fig5 = px.bar(
            fund_df,
            x='Fund Type',
            y=['Avg 3Y Return (%)',
               'Avg 5Y Return (%)'],
            title='3Y vs 5Y Returns by Fund',
            barmode='group',
            color_discrete_sequence=[
                '#3498db', '#2ecc71']
        )
        fig5.update_layout(
            height=400,
            template='plotly_white'
        )
        fig5.update_xaxes(tickangle=45)
        st.plotly_chart(fig5,
                        use_container_width=True)

    with col2:
        # SIP comparison
        sip_compare = st.number_input(
            "Monthly SIP to compare (₹):",
            value=5000,
            step=1000
        )
        compare_years = st.slider(
            "Years:", 5, 30, 10,
            key="compare_years")

        comp_results = []
        for _, row in fund_df.iterrows():
            rate     = row['Avg 5Y Return (%)']
            m_rate   = rate / 100 / 12
            months   = compare_years * 12
            fv       = sip_compare * (
                ((1 + m_rate) ** months - 1)
                / m_rate
            ) * (1 + m_rate)
            invested = sip_compare * months
            comp_results.append({
                'Fund':      row['Fund Type'],
                'Value (₹L)':round(fv/1e5, 1),
                'Gain (₹L)': round(
                    (fv-invested)/1e5, 1)
            })

        comp_results_df = pd.DataFrame(
            comp_results).sort_values(
            'Value (₹L)', ascending=False)

        fig6 = px.bar(
            comp_results_df,
            x='Value (₹L)',
            y='Fund',
            orientation='h',
            title=f'₹{sip_compare:,}/mo SIP '
                  f'after {compare_years}yrs',
            color='Value (₹L)',
            color_continuous_scale='Greens'
        )
        fig6.update_layout(
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig6,
                        use_container_width=True)

    st.dataframe(fund_df,
                 use_container_width=True,
                 hide_index=True)

    st.caption(
        "⚠️ Returns shown are historical "
        "averages. Past performance does not "
        "guarantee future returns. "
        "Consult a financial advisor.")

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "SIP & Investment Calculator | "
    "For educational purposes only"
)