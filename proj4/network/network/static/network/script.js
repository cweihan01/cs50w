document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM content loaded.")
    
    // Run only on profile page
    if (window.location.href.indexOf("profile/") > -1) {
        // Get profile username - idk whether getting it from the header is a good idea
        const username = document.querySelector("#profileUsername").innerHTML
        console.log("username: ", username)
        
        // Get following and follower count
        // From `profile/username` path, `fetch` will request relative path `profile/...`
        fetch(`${username}/follow`, {
            method: "GET"
        })
        .then(response => response.json())
        .then(profile => {
            // `profile` is an object with 2 objects: `following` and `followers`
            // `following` and `followers` both contain an array of `User` id
            console.log(`User profile of ${username} fetched: `, profile)
            
            // Dynamically insert following and follower count
            document.querySelector("#followersCount").innerHTML = profile.followers.length
            document.querySelector("#followingCount").innerHTML = profile.following.length
            
            // Update followButton dynamically, only if user is logged in
            if (profile.user_logged_in) {
                if (profile.is_following) {
                    document.querySelector("#followButton").innerHTML = "Unfollow"
                } else {
                    document.querySelector("#followButton").innerHTML = "Follow"
                }
                
                document.querySelector("#followButton").onclick = () => {
                    fetch(`${username}/follow`, {
                        method: "PUT"
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log(`Following ${username}?`, data)
                        const followButton = document.querySelector("#followButton")
                        if (data.is_following) {
                            followButton.innerHTML = "Unfollow"
                            document.querySelector("#followersCount").innerHTML++
                        } else {
                            followButton.innerHTML = "Follow"
                            document.querySelector("#followersCount").innerHTML--
                        }   
                    })
                }
            }
        })
    }
    
    // Handle all edit-buttons
    document.querySelectorAll(".edit-buttons").forEach(button => {
        // Get the Post that is being edited
        const post_id = parseInt(button.dataset.id)
        
        // Add event listener to each button
        button.addEventListener("click", () => {
            console.log(`editButton${post_id} clicked`)
            
            // Disable all other edit-buttons until current edit submitted
            document.querySelectorAll(".edit-buttons").forEach(button => {
                button.disabled = true
            })
            
            // Fetch Post data and handle editPost view
            fetch(`posts/edit/${post_id}`, {
                method: "GET"
            })
            .then(response => response.json())
            .then(post => {
                console.log(`Post ${post_id} fetched from database: `, post)
                
                // Hide post view and display edit form
                document.querySelector(`#viewPost${post_id}`).style.display = "none"
                document.querySelector(`#editPost${post_id}`).style.display = "block"
                
                // Pre-fill edit form from database
                document.querySelector(`#editTitle${post_id}`).value = post.title
                document.querySelector(`#editContents${post_id}`).value = post.contents
                
                // Handle submit - call another function
                document.querySelector(`#editPost${post_id}`).onsubmit = () => {
                    // Hide edit form and display new updated post
                    document.querySelector(`#viewPost${post_id}`).style.display = "block"
                    document.querySelector(`#editPost${post_id}`).style.display = "none"
                    
                    // Access form data
                    const title = document.querySelector(`#editTitle${post_id}`).value
                    const contents = document.querySelector(`#editContents${post_id}`).value
                    
                    // Update edited post in database
                    fetch(`posts/edit/${post_id}`, {
                        method: "POST",
                        body: JSON.stringify({
                            title: title,
                            contents: contents
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log("Form submitted, data retrieved: ", data)
                        
                        // Once database updated, update HTML that user sees
                        document.querySelector(`#viewTitle${post_id}`).innerHTML = title
                        document.querySelector(`#viewContents${post_id}`).innerHTML = contents
                        // How to render this directly from model datetimefield without converting manually?
                        document.querySelector(`#viewModified${post_id}`).innerHTML = data.post.modified
                        
                        console.log("Edits to post completed.")
                    })
                    
                    // Enable all other edit-buttons once form submitted
                    document.querySelectorAll(".edit-buttons").forEach(button => {
                        button.disabled = false
                    })
                    
                    // Prevent form from submitting
                    return false;
                }
            })
        })
    })    
})
