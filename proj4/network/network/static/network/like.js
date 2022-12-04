// Handles the Like button on posts
document.addEventListener("DOMContentLoaded", () => {
    
    // Iterate through each heart/post on page
    document.querySelectorAll(".post-heart").forEach(heart => {
        const post_id = parseInt(heart.dataset.id)
    
        // Loads hearts when page is loaded - either liked (red) or unliked (white)
        fetch(`/posts/like/${post_id}`, {
            method: "GET"
        })
        .then(response => response.json())
        .then(data => {
            // Update likes on each post
            if (data.is_liked) {
                document.querySelector(`#likeHeart${post_id}`).innerHTML = "&#10084;" // red heart
            } else {
                document.querySelector(`#likeHeart${post_id}`).innerHTML = "&#9825;" // white
            }
            document.querySelector(`#likeCount${post_id}`).innerHTML = data.like_count

            if (data.like_count > 0) {
                document.querySelector(`#likeBy${post_id}`).style.display = "block"
                document.querySelector(`#likeUsers${post_id}`).innerHTML = data.liked_by
            }
        })

        // Handles when a like button is pressed
        heart.addEventListener("click", () => {
            console.log(`Like on post ${post_id} clicked`)

            fetch(`/posts/like/${post_id}`, {
                method: "PUT"
            })
            .then(response => response.json())
            .then(data => {
                // Error if anonymous user tries to like a post
                if (data.error) {
                    throw new Error(data.error)
                }
                
                // Update client side when user likes a post - increase like count and emoji
                if (data.post_liked) {
                    document.querySelector(`#likeHeart${post_id}`).innerHTML = "&#10084;" // red heart
                    document.querySelector(`#likeCount${post_id}`).innerHTML++
                } else {
                    document.querySelector(`#likeHeart${post_id}`).innerHTML = "&#9825;" // white
                    document.querySelector(`#likeCount${post_id}`).innerHTML--
                }
            })
            .catch(error => {
                alert(error.message)
            })
        })
    })
})