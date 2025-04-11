document.addEventListener('DOMContentLoaded', function(){
    const productLinks = document.querySelector('.product-link')
    console.log("HIIII")
    productLinks.addEventListener('click', function(event){
        event.preventDefault();
        const isbn = this.getAttribute('data-isbn')
        console.log(isbn)
        const href = this.href

        //registerInteraction(isbn, 'click');

        setTimeout(() => {
            window.location.href = href
        }, 10000);
    })
})



function registerInteraction(isbn, interactionType, timeSpent = 0)
{
    console.log('websocket connected')
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/interaction/${isbn}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken':csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            [interactionType]: true,
            'time_spent': timeSpent,
        })
    }).then(response => response.json()).then(data => {
        console.log('Interaction Value:', data.rating);
    })
}


// Tracking time spent on the book page
let startTime;
document.addEventListener('DOMContentLoaded', () => {
    const timeSpentStart = document.querySelectorAll('.product-link')

    timeSpentStart.addEventListener('click', function(){
        startTime = new Date() //Start the timer when a book is viewed
    })

    timeSpentEnd.addEventListener('scroll', function(){
        let endTime = new Date();
        let timeSpent = (endTime-startTime) / 1000; // Time spent in seconds
        let isbn = this.getAttribute('data-isbn')

        registerInteraction(isbn, 'click', timeSpent)
    })
})