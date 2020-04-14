function doSomething() {
    var ele = document.getElementById("searchTerm");
    ele.value = ele.value.replace(/'/g,"''");
}