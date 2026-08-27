let currentStock = "";
let currentPrice = "";
let position_id="";
let socket=null;

let activePositions = {};

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
   
    
    socket.onopen = () => {
        console.log("[websocket] connected successfully");
    };
    
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WS RECEIVED:", data);
        
        switch(data.type) {
            case "ACTIVE_POSITIONS":
                // 1. Initial baseline payload containing all running instances
                activePositions = {};
                data.positions.forEach(position => {
                    if (position.status === "ACTIVE") {
                        activePositions[position.stock] = position;
                    }
                });
                renderDashboard(); 
                break;

            case "PRICE_UPDATE":
                // 2. Real-time updates pushed from backend TSL mathematical engine
                if (data.position && data.position.status === "ACTIVE") {
                    const incomingPos = data.position;
                    
                    // Update client memory map
                    activePositions[incomingPos.stock] = incomingPos;
                    
                    // Re-draw UI view only if user is actively tracking this stock's panel
                    if (currentStock === incomingPos.stock) {
                        renderDashboard();
                    }
                }
                break;

            case "EXIT TSL":
                // 3. Triggered when backend rules flag a hard TSL cross 
                if (data.position) {
                    const droppedPos = data.position;
                    console.warn(`[Risk Management Action] Evicting asset via trailing stop execution: ${droppedPos.stock}`);
                    
                    // Clear out our operational state dictionary context
                    delete activePositions[droppedPos.stock];
                    
                    // Re-render immediately (dashboard will automatically toggle to style.display = 'none')
                    if (currentStock === droppedPos.stock) {
                        renderDashboard();
                    }
                }
                break;
                
            default:
                console.log("Context packet unmapped or falling outside active telemetry boundaries:", data.type);
        }
    };

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
                
                // === FIX: Re-render dashboard on stock/price change ===
                renderDashboard(); 

                const activePosition = activePositions[currentStock];
                if (activePosition) {
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
// Add these changes to your existing watcher.js file

function initClickTracker() {
    document.addEventListener('click', (event) => {
        const clickedElement = event.target;
        
        // 1. Check if the trader clicked your custom manual close button
        const exitButton = clickedElement.closest('.manual-exit-btn');
        if (exitButton) {
            event.preventDefault();
            event.stopImmediatePropagation();
            
            const targetId = exitButton.getAttribute('data-position-id');
            console.log(`[Manual Exit Triggered] Requesting liquidation for ID: ${targetId}`);
            
            toBackendManualExit({ "position_id": targetId });
            return; // Exit tracker so it doesn't process regular order checks
        }

        // 2. Regular TradingView order execution pipeline
        const buttonArea = clickedElement.closest('button') || clickedElement;
        const innerText = buttonArea.innerText ? buttonArea.innerText.toUpperCase() : "";
       
        let actionWord = "";
        if (innerText.includes('BUY')) {
            actionWord = 'BUY';
        } else if (innerText.includes('SELL')) {
            actionWord = 'SELL';
        }
        if (!actionWord) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        const payload = {
            "stock": currentStock,
            "price": currentPrice,
            "action": actionWord
        };
        console.log(`[Order Triggered] Sending:`, payload);
        toBackend(payload);
    }, true);
}

// REST Network Call for Liquidation Requests
async function toBackendManualExit(payload) {
    try {
        const response = await fetch('http://localhost:8000/manual-exit', {
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
        console.log("[Backend Exit Response]", responseData);
    } catch (error) {
        console.error(`[Connection Error] Liquidation command failed: ${error.message}`);
    }
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
        console.log("[Backend Response]", responseData);
    } catch (error) {
        console.error(`[Connection Error] Failed to send order: ${error.message}`);
    }
}
