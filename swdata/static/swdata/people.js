var loadMoreBtn = document.getElementById("data-load-btn")
var filename = document.getElementById("filename-header").innerHTML
var dataContainer = document.getElementById("data-container")

var visible = 0 
var max_size = Number.MAX_VALUE

const getData = () => {
    fetch(`/people/load/${filename}?beg=${visible}&end=${visible + 10}`, {
        method: "GET",
        headers: {
            "Content-Type" : "application/json"
          },
    })
    .then(response => response.json())
    .then(json => {
        var data = JSON.parse(json.data)
        var dataHtml = ""
        data.map(person => {
            dataHtml += `<tr>`
            person.map(field => {
                dataHtml += `<td>${field}</td>`
            })
            dataHtml += `</tr>`      
        })
        dataContainer.innerHTML += dataHtml
        max_size = json.max_size
    });
}

getData()
visible += 10

loadMoreBtn.addEventListener('click', ()=>{
    if(visible < max_size) {
        getData()
        visible += 10
    }
})