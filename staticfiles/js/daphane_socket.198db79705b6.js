    /*const socket = new WebSocket('ws://' + window.location.host + '/ws/interaction/');
    console.log('connected')
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data) {
            console.log('data')
        }
        console.log(data, 'Data is absent')

        if (data.status === 'success') {
            if (data.rating) {
                // Update rating in the UI
                document.getElementById('rating').innerText = `Rating: ${data.rating}`;
            }

            if (data.recommendations) {
                // Update recommendations in the UI
                const recommendationsList = document.getElementById('recommendations');
                recommendationsList.innerHTML = '';

                data.recommendations.forEach(book => {
                    const li = document.createElement('li');
                    li.innerText = `${book.title} (ISBN: ${book.isbn})`;
                    recommendationsList.appendChild(li);
                });
            }
        }
    };

    function registerInteraction(isbn, action, time_spent = 0) {
        socket.send(JSON.stringify({
            'isbn': isbn,
            'action': action,
            'time_spent': time_spent
        }));
    }

        // Example: Register a 'like' interaction when the like button is clicked
    document.getElementById('like-button').addEventListener('click', function() {
        registerInteraction('{{ product.isbn }}', 'like');
    });

    // Example: Register an 'add to cart' interaction when the add to cart button is clicked
    document.getElementById('add-to-cart-button').addEventListener('click', function() {
        registerInteraction('{{ product.isbn }}', 'add_to_cart');
    });
    
            // Example: Track time spent on the product page
    /*let startTime = Date.now();
    //window.addEventListener('beforeunload', function() {
     //   let timeSpent = (Date.now() - startTime) / 1000; // Convert to seconds
       // registerInteraction('{{ product.isbn }}', 'click', time_spent = timeSpent);
    //});

    //onclick="registerInteraction('{{product.isbn}}', 'like')" */
