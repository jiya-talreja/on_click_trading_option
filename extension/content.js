window.addEventListener('load',()=>{
    console.log("page is loaded")
    document.addEventListener('click',(event)=>{
        closeButton=event.target
        nearArea=closeButton.closest('button') || closeButton
        console.log(nearArea);
        innerword=nearArea.innerText ? nearArea.innerText.toUpperCase() : ""
        console.log(innerword);  
        let actionword=""
        if(innerword.includes('BUY')){
            actionword='BUY'
        }      
        else if(innerword.includes('SELL')){
            actionword='SELL'
        }
        console.log(actionword);
        if(innerword.includes('BUY')){
            actionword='BUY'
        }
        else if(innerword.includes('SELL')){
            actionword='SELL'
        }
        let activestock = "";
        if(actionword!=""){
            console.log(actionword)
            const possname=document.title
            const possiblename=document.title.trim()
            console.log(possname,possiblename)
            const titlepart=possiblename.split(/\s+/)
            console.log(titlepart)
            activestock=titlepart[0]
            console.log(activestock)
        }
        else{
            console.log("error")
        }
        const backend={
            "stock":activestock,
            "action":actionword
        }
        console.log(backend.stock,backend.action);
        if(actionword === ""){
            return;
        }
        tobackend(backend);
    })
})

async function tobackend(backend) {
    try{
        const reponse=await fetch('http://localhost:8000/trade',{
            method :'POST',
            headers : {
                'content-type':'application/json'
            },
            body : JSON.stringify(backend)
        })
        if(!reponse.ok){
            throw new Error(`status unsure ${reponse.status}`)
        }
        const data=await reponse.json()
        console.log(data);
    }catch(error){
        console.error(`error ${error.message}`);
    }
}
