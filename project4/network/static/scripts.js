
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

        document.addEventListener('DOMContentLoaded', (event) => {
            const likeButton = document.getElementById('like-button');
            const likeCountSpan = likeButton.querySelector('.like-count');
          
            likeButton.addEventListener('click', function() {
              const postId = this.getAttribute('data-post-id');
              const isLiked = this.getAttribute('data-liked') === 'true';
              const newLikeCount = parseInt(likeCountSpan.textContent, 10) + (isLiked ? -1 : 1);
          
              // Update the like count and toggle the data-liked attribute
              likeCountSpan.textContent = newLikeCount;
              this.setAttribute('data-liked', !isLiked);
          
              // Here you would also send a fetch request to your server to update the like status
              // fetch(`/toggle_like/${postId}`, { ... });
            });
          });
    