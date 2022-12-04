document.addEventListener("DOMContentLoaded", () => {
    
    // Get profile username - idk whether getting it from the header is a good idea
    const username = document.querySelector("#profileUsername").innerHTML
    console.log("username: ", username)
    
    // Get following and follower count
    // From `profile/username` path, `fetch` will request relative path `profile/...`
    // unless leading slash present - `/profile/...` will be relative to domain root
    fetch(`/profile/${username}/follow`, {
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
})