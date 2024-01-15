function upvote(postId) {
    fetch('/upvote/' + postId, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        document.getElementById('upvote-count-' + postId).innerText = 'Upvotes: ' + data.upvotes;
        let btn = document.getElementById('upvote-btn-' + postId);
        if (data.upvoted) {
            btn.classList.add('upvoted');
        } else {
            btn.classList.remove('upvoted');
        }
    })
    .catch(error => console.error('Error:', error));
    console.log('asdasdasda');
}