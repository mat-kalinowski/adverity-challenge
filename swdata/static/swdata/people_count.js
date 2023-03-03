var filename = document.getElementById("filename-header").innerHTML
var dataContainer = document.getElementById("data-container")

function toggleParameter(event) {   
    event = event || window.event;
    var source = event.target || event.srcElement || event; 

    if(source.dataset.state == "on") {
        source.dataset.state = "off"
        source.className = "btn btn-outline-secondary m-1"
    } else {
        source.dataset.state = "on"
        source.className = "btn btn-outline-primary m-1"
    }

    var queryString = `/count/load/${filename}?params=`
    var child_arr = [...source.parentElement.children]
    var params = ''

    child_arr.forEach(node => {
        if(node.dataset.state == "on") params += node.innerHTML + ","
    })

    if (params == '') return

    queryString += params
    queryString = queryString.substring(0, queryString.length - 1);

    fetch(queryString, {
        method: "GET",
        headers: {
            "Content-Type" : "application/json"
          },
    })
    .then(response => response.json())
    .then(json => {        
        var data = JSON.parse(json.data)
        var header = JSON.parse(json.header)
        var dataHtml = '<thead class="thead-dark"><tr>'
        header.map(field => {
            dataHtml += `<th>${field}</th>`
        })

        dataHtml += '</tr></thead>'
        data.map(row => {
            dataHtml += `<tr>`
            row.map(field => {
                dataHtml += `<td>${field}</td>`
            })
            dataHtml += `</tr>`      
        })
        dataContainer.innerHTML = dataHtml
    });
}