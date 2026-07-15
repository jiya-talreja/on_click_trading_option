let currentStock = "";
let currentPrice = "";
let position_id="";
let socket=null;
let activestockwatch={};
window.addEventListener('load', () => {
    console.log("TradingView automation extension loaded.");
    initialwebsocket();
    initMasterTitleObserver();
    initClickTracker();
});
function initialwebsocket(){
    socket=new WebSocket('ws://localhost:8000/trade-stream')
    socket.onopen=()=>{
        console.log("[websocket] connected sucessfully")
    }
    socket.onmessage=(event)=>{
        console.log("MESSAGE FROM BACKEND : ",event.data);
    }
    socket.onclose = () => {
        console.warn("[WebSocket] Disconnected. Reconnecting in 3 seconds...");
        setTimeout(initialwebsocket, 3000);
    };
    socket.onerror = (error) => {
        console.error("[WebSocket Error]:", error);
    };
}
function initMasterTitleObserver() {
    const parseTitleData = () => {
        const titleText = document.title.trim()
        const titleParts = titleText.split(/\s+/);
        console.log("ttitlepart : ",titleParts);
        if (titleParts.length >= 2) {
            currentStock = titleParts[0];
            console.log(currentStock)
            const rawPrice = titleParts[1];
            console.log(rawPrice);
            const cleanPrice = rawPrice.replace(/[^0-9.]/g, ''); 
            console.log(cleanPrice);
            if (cleanPrice && !isNaN(cleanPrice)) {
                currentPrice = cleanPrice;
                console.log(`[Master Watcher] Updated -> ${currentStock} @ ${currentPrice}`); // Debug
                const activePosition = activestockwatch[currentStock];
                if (activePosition && activePosition.order_status === "FILLED") {
                    streamPriceUpdate(activePosition.position_id, currentStock, currentPrice);
                }
            }
        }
    };
    parseTitleData();
    const titleTarget = document.querySelector('title');
    if (titleTarget) {
        const observer = new MutationObserver(parseTitleData);
        observer.observe(titleTarget, { childList: true });
        console.log("[Master Watcher] Actively syncing live values from title tracking.");
    }
}
function initClickTracker() {
    document.addEventListener('click', (event) => {
        const clickedElement = event.target;
        const buttonArea = clickedElement.closest('button') || clickedElement;
        const innerText = buttonArea.innerText ? buttonArea.innerText.toUpperCase() : "";
       
        let actionWord = "";
        if (innerText.includes('BUY')) {
            actionWord = 'BUY';
        } else if (innerText.includes('SELL')) {
            actionWord = 'SELL';
        }
        if (!actionWord) return;
        const payload = {
            "stock": currentStock,
            "price": currentPrice,
            "action": actionWord
        };
        console.log(`[Order Triggered] Sending:`, payload);
        toBackend(payload);
    });
}
function streamPriceUpdate(positionId, stock, price) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const pricePayload = {
            "type": "PRICE_UPDATE",
            "position_id": positionId,
            "stock": stock,
            "current_price": parseFloat(price)
        };
        socket.send(JSON.stringify(pricePayload));
        console.log(`[Stream -> Redis] ${stock} (${positionId}) @ ${price}`);
    }
}
async function toBackend(payload) {
    if (!payload.stock || !payload.price) {
        console.error("[Backend Error] Blocked send: Missing stock ticker or live price.");
        return;
    }
    try {
        const response = await fetch('http://localhost:8000/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }
        const responseData = await response.json();
        const context = responseData.trade;
        if (context.order_status === "FILLED") {
        activestockwatch[context.stock] = {
            position_id: context.position_id,
            order_status: context.order_status,
            action: context.action
        };
        console.log("[WATCHING STARTED]", activestockwatch);
        }
        console.log("[Backend Response]", responseData);
    } catch (error) {
        console.error(`[Connection Error] Failed to send order: ${error.message}`);
    }
}
