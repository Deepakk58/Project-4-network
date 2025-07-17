document.addEventListener('DOMContentLoaded', function() {
    const textArea = document.querySelector('.newPost');
    if (textArea) {

        const submit = document.querySelector('.postButton');
        submit.disabled = true;

        textArea.addEventListener('input', function() {
            const raw = textArea.value;
            const trimmed = textArea.value.trim();

            const counter = document.querySelector('.postLen')
            if (trimmed.length > 300) {
                textArea.value = trimmed.substring(0, 300);
                counter.innerHTML = `300/300`;
            }
            else {
                textArea.value = raw.trimStart()
                counter.innerHTML = `${trimmed.length}/300`;
            }

            submit.disabled = trimmed.length === 0;
        });
    }
    const forms = document.querySelectorAll('.editPost');

    forms.forEach(form => {                

        form.addEventListener('input', function() {

            const raw = form.value;
            const trimmed = raw.trim();

            const box = form.parentElement.parentElement;
            const counter = box.querySelector('.editLen');
            
            if (trimmed.length > 300) {
                form.value = trimmed.substring(0, 300);
                counter.innerHTML = `300/300`;
            }
            else {
                form.value = raw.trimStart()
                counter.innerHTML = `${trimmed.length}/300`;
            }

            const submit = box.querySelector('.editButton');
            
            submit.disabled = trimmed.length === 0;
        })
    });
})

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function edit(id) {
    const post = document.querySelector(`#post_${id}`);
    const form = document.querySelector(`#post_${id}form`);
    post.style.display = "none";
    form.style.display = "block";
    
    const counter = form.querySelector('.editLen');
    
    Msg = post.querySelector('.post-content').innerHTML.trim();
    counter.innerHTML = `${Msg.length}/300`;
    
    document.querySelector(`#editedContent_${id}`).value = Msg;
}

function cancel(id) {
    document.querySelector(`#post_${id}`).style.display = "block";
    document.querySelector(`#post_${id}form`).style.display = "none";
    document.querySelector(`#editedContent_${id}`).value = "";
}

function save(id, event) {
    event.preventDefault();
    const text = document.querySelector(`#editedContent_${id}`).value;
    const post = document.querySelector(`#post_${id} .post-content`);

    fetch(`/edit/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            content: text
        })
    })
    .then(response => response.json())
    .then(result => {  
        post.innerHTML = result.data;              
        document.querySelector(`#post_${id}`).style.display = "block";
        document.querySelector(`#post_${id}form`).style.display = "none";
    })
}

function deletePost(id) {
    
    const confirmed = confirm("Are you sure you want to delete this post?");
    if (!confirmed) {
        return;
    }
    
    const post = document.querySelector(`#post_${id}box`);
    fetch(`/delete/${id}/`)
    .then(response => response.json())
    .then(result => {  
        post.classList.add('hideclass')
        post.addEventListener('animationend', () =>  {
            post.remove();
        });
    })
}

function like(id, liked) {
    const btn = document.querySelector(`#like_${id}`);
    const counter = document.querySelector(`#counter_${id}`);
    let likes = parseInt(counter.innerHTML);
    
    btn.classList.remove('fa-solid');
    btn.classList.remove('fa-regular');

    if (liked === true) {
        fetch(`/unlike/${id}/`)
        .then(response => response.json())
        .then(result => {
            likes--;
            counter.innerHTML = likes;
            btn.classList.add('fa-regular');
            btn.setAttribute("onclick", `like(${id}, false)`);
        })
    }
    else {
        fetch(`/like/${id}/`)
        .then(response => response.json())
        .then(result => {
            likes++;
            counter.innerHTML = likes;
            btn.classList.add('fa-solid');
            btn.setAttribute("onclick", `like(${id}, true)`);
        })
    }
}