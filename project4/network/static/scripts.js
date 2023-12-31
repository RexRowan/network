
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length == 2) return parts.pop().split(';').shift();
        }

        function submitHandler(id) {
            const textareaValue = document.getElementById(`textarea_${id}`).value;
            const content = document.getElementById(`content_${id}`);
            const modal = document.getElementById(`modal_edit_post_${id}`);
            fetch(`/edit/${id}`, {
                method: "POST",
                headers: {
                    "Content-type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    content: textareaValue
                })
            })
                .then(response => response.json())
                .then(result => {
                    content.innerHTML = result.data;

                    modal.classList.remove('show');
                    modal.setAttribute('aria-hidden', 'true');
                    modal.setAttribute('style', 'display: none');

                // get modal backdrops
                    const modalsBackdrops = document.getElementsByClassName('modal-backdrop');

                    for (let i = 0; i < modalsBackdrops.length; i++) {
                        document.body.removeChild(modalsBackdrops[i]);
                    }
                })

        }

        function toggleLike(postId) {
            const likeButton = document.getElementById(`like-btn-${postId}`);
            const likeCountSpan = document.getElementById(`like-count-${postId}`);

            if (!likeButton || !likeCountSpan) {
                console.error('One or more elements do not exist.');
                return;
            }

            fetch(`/toggle_like/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(result => {
                // Update the like count and button text based on the new like status
                likeCountSpan.textContent = result.new_like_count;
                likeButton.textContent = result.liked ? 'Unlike' : 'Like';
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    