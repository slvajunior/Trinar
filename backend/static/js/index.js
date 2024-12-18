document.addEventListener('DOMContentLoaded', function () {
    // Configuração do CSRF Token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // Botões de like
    const likeButtons = document.querySelectorAll('.btn-like');
    likeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const postId = this.getAttribute('data-post-id');
            const likeCountSpan = this.querySelector('.like-count');

            fetch('/toggle-like/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `post_id=${postId}`
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                    } else {
                        likeCountSpan.textContent = data.likes_count;
                        button.classList.toggle('active', data.user_has_liked);
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });

    // Botões de comentário
    const commentButtons = document.querySelectorAll('.comment-btn');
    commentButtons.forEach(button => {
        button.addEventListener('click', function () {
            const postId = this.getAttribute('data-post-id');
            const modal = document.getElementById(`comment-modal-${postId}`);
            if (modal) modal.showModal();
        });
    });

    // Fechar modais
    const closeModalButtons = document.querySelectorAll('.close-modal');
    closeModalButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = button.closest('dialog');
            if (modal) modal.close();
        });
    });
});

// Scroll da tela mais rápido

// Selecionando o elemento da timeline
const timeline = document.querySelector('.timeline');

// Função para calcular a velocidade da rolagem com base na largura da tela
function getScrollSpeed() {
    const screenWidth = window.innerWidth;

    // A velocidade da rolagem aumenta conforme a largura da tela
    if (screenWidth > 1200) {
        return 50; // Mais rápido em telas grandes
    } else if (screenWidth > 768) {
        return 30; // Velocidade média para tablets
    } else {
        return 15; // Mais devagar em dispositivos móveis
    }
}

// Adicionando um ouvinte de evento para o scroll da página
window.addEventListener('wheel', function(event) {
    // Verifica se o evento de scroll não é disparado sobre a timeline
    if (!timeline.contains(event.target)) {
        // Impede o comportamento padrão do evento de rolagem (scroll na página)
        event.preventDefault();

        // Obtém a velocidade da rolagem de acordo com o tamanho da tela
        const scrollSpeed = getScrollSpeed();

        // Rolagem manual na timeline
        if (event.deltaY > 0) {
            // Se o scroll for para baixo, rola para baixo
            timeline.scrollTop += scrollSpeed;
        } else {
            // Se o scroll for para cima, rola para cima
            timeline.scrollTop -= scrollSpeed;
        }
    }
}, { passive: false });

document.addEventListener("DOMContentLoaded", function () {
    // Seleciona todas as seções de conteúdo do post
    const posts = document.querySelectorAll(".post-content");

    posts.forEach(post => {
        const textElement = post.querySelector("p");
        const content = textElement.innerHTML || textElement.innerText; // Mantém o conteúdo com HTML

        // Remover conteúdo HTML (links e hashtags) para medir apenas o texto simples
        const textOnly = textElement.innerText || content.replace(/<[^>]+>/g, ''); // Remove todas as tags HTML

        if (textOnly.length <= 55) {
            // Textos com até 55 caracteres: Fonte maior
            textElement.classList.add("short");
        } else if (textOnly.length <= 220) {
            // Textos entre 56 e 100 caracteres: Fonte intermediária
            textElement.classList.add("medium");
        } else {
            // Textos longos com mais de 100 caracteres
            const originalContent = content; // Salva o conteúdo original, incluindo links e hashtags
            const truncatedContent = content.slice(0, 180) + "..."; // Trunca a partir de 55 caracteres
            textElement.innerHTML = truncatedContent; // Usa innerHTML para preservar os links

            textElement.classList.add("long");

            // Cria o botão "Ler mais"
            const readMoreButton = document.createElement("button");
            readMoreButton.classList.add("read-more-btn");
            readMoreButton.textContent = "Ler mais";
            post.appendChild(readMoreButton);

            // Adiciona evento de clique ao botão
            let isExpanded = false;
            readMoreButton.addEventListener("click", () => {
                if (isExpanded) {
                    textElement.innerHTML = truncatedContent; // Volta ao texto truncado, mantendo os links
                    readMoreButton.textContent = "Ler mais";
                    isExpanded = false;
                } else {
                    textElement.innerHTML = originalContent; // Mostra o texto completo, incluindo links
                    readMoreButton.textContent = "Mostrar menos";
                    isExpanded = true;
                }
            });
        }
    });
});
