function createDashboard() {
    let dashboard = document.getElementById("algo-dashboard");

    if (dashboard) return dashboard;

    dashboard = document.createElement("div");
    dashboard.id = "algo-dashboard";

    dashboard.style.cssText = `
    position: fixed;
    top: 68px;
    left: 50%;
    transform: translateX(-50%);

    display: flex;
    align-items: center;
    gap: 14px;

    height: 36px;
    padding: 0 12px;

    background: rgba(45, 49, 66, 0.72);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);

    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 7px;

    box-shadow:
        0 2px 8px rgba(0, 0, 0, 0.18),
        0 0 0 1px rgba(0, 0, 0, 0.05);

    color: #d1d4dc;

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        sans-serif;

    font-size: 13px;
    font-weight: 500;

    z-index: 9999;

    pointer-events: none;

    white-space: nowrap;
`;
    document.body.appendChild(dashboard);

    return dashboard;
}


function renderDashboard() {

    const dashboard = createDashboard();

    const position = activePositions[currentStock];

    /*
     * No active position -> hide overlay.
     */
    if (!position || position.status !== "ACTIVE") {

        dashboard.style.display = "none";

        return;
    }

    dashboard.style.display = "flex";

    renderPositionCard(position);
}


function renderPositionCard(position) {

    const dashboard =
        document.getElementById("algo-dashboard");

    if (!dashboard) return;


    /*
     * ==========================================
     * BASIC VALUES
     * ==========================================
     */

    const entryPrice =
        Number(position.entry_price) || 0;

    const currentPriceFloat =
        Number(position.current_price) ||
        Number(currentPrice) ||
        0;

    const stopLoss =
        Number(position.stop_loss) || 0;

    const trailingStop =
        Number(position.trailing_stop) || 0;


    /*
     * ==========================================
     * BUY / SELL
     * ==========================================
     */

    const isBuy =
        position.action === "BUY";


    const actionColor =
        isBuy
            ? "#26a69a"
            : "#ef5350";


    const actionBackground =
        isBuy
            ? "rgba(38, 166, 154, 0.16)"
            : "rgba(239, 83, 80, 0.16)";


    /*
     * ==========================================
     * P&L
     * ==========================================
     */

    let pnlPercent = 0;

    if (entryPrice > 0) {

        pnlPercent = isBuy
            ? ((currentPriceFloat - entryPrice)
                / entryPrice) * 100

            : ((entryPrice - currentPriceFloat)
                / entryPrice) * 100;
    }


    const pnlPositive =
        pnlPercent >= 0;


    const pnlColor =
        pnlPositive
            ? "#26a69a"
            : "#ef5350";


    const pnlBackground =
        pnlPositive
            ? "rgba(38, 166, 154, 0.15)"
            : "rgba(239, 83, 80, 0.15)";


    /*
     * ==========================================
     * DASHBOARD
     * ==========================================
     */

    dashboard.innerHTML = `
    <div style="
        display: flex;
        align-items: center;
        gap: 7px;
        padding-right: 12px;
        border-right: 1px solid rgba(255,255,255,0.14);
        pointer-events: auto;
    ">
        <span style="
            background: ${actionBgColor};
            color: ${actionTextColor};
            font-size: 11px;
            font-weight: 800;
            padding: 3px 7px;
            border-radius: 4px;
            letter-spacing: 0.3px;
        ">
            ${position.action}
        </span>

        <span style="
            color: #aeb4c0;
            font-size: 12px;
            font-weight: 600;
        ">
            Qty: ${position.quantity}
        </span>
    </div>


    <div style="
        display: flex;
        align-items: center;
        gap: 15px;
        font-size: 13px;
    ">

        <div>
            <span style="color:#9aa0aa;">Entry:</span>
            <strong style="
                color:#f0f3fa;
                font-weight:700;
            ">
                ₹${entryPrice.toFixed(2)}
            </strong>
        </div>

        <div>
            <span style="color:#9aa0aa;">LTP:</span>
            <strong style="
                color:#26a69a;
                font-weight:800;
            ">
                ₹${currentPriceFloat.toFixed(2)}
            </strong>
        </div>

        <div>
            <span style="color:#9aa0aa;">SL:</span>
            <strong style="
                color:#ffb74d;
                font-weight:800;
            ">
                ₹${parseFloat(position.stop_loss).toFixed(2)}
            </strong>
        </div>

        <div>
            <span style="color:#9aa0aa;">TSL:</span>
            <strong style="
                color:#ff6b5f;
                font-weight:800;
            ">
                ₹${parseFloat(position.trailing_stop).toFixed(2)}
            </strong>
        </div>

    </div>


    <div style="
        background:${pnlBgColor};
        color:${pnlColor};

        font-weight:800;
        font-size:12px;

        padding:3px 8px;
        border-radius:4px;

        min-width:55px;
        text-align:center;

        border:1px solid ${pnlColor}33;
    ">
        ${pnlPercent >= 0 ? '+' : ''}${pnlPercent.toFixed(2)}%
    </div>


    <button
        class="manual-exit-btn"
        data-position-id="${position.position_id}"
        style="
            pointer-events:auto;

            background:#ef5350;
            color:#ffffff;

            border:1px solid rgba(255,255,255,0.12);
            border-radius:4px;

            padding:3px 10px;

            font-weight:800;
            font-size:12px;

            cursor:pointer;

            height:24px;

            display:flex;
            align-items:center;

            transition:
                background 0.15s,
                transform 0.1s;
        "

        onmouseover="
            this.style.background='#d32f2f';
        "

        onmouseout="
            this.style.background='#ef5350';
        "
    >
        Exit
    </button>
`;
}
