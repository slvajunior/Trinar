// Selecionando o elemento da timeline
const timeline = document.querySelector('.timeline');

// Função para calcular a velocidade da rolagem com base na largura da tela
function getScrollSpeed() {
    const screenWidth = window.innerWidth;

    // Velocidade de rolagem adaptada à largura da tela e taxa de atualização
    if (screenWidth > 1200) {
        return 50;  // Rápida para telas grandes (1920x1080)
    } else if (screenWidth > 768) {
        return 30;  // Média para telas médias (tablets)
    } else {
        return 15;  // Lenta para telas pequenas (dispositivos móveis)
    }
}

// Adicionando um ouvinte de evento para o scroll da página
window.addEventListener('wheel', function (event) {
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

document.addEventListener('DOMContentLoaded', function () {
    const textareas = document.querySelectorAll('textarea[name="content"]');

    textareas.forEach(textarea => {
        textarea.addEventListener('input', function () {
            const maxCharsPerLine = 500; // Máximo de caracteres por linha
            const caretPosition = this.selectionStart; // Posição atual do cursor

            const lines = this.value.split('\n').map(line => {
                if (line.length > maxCharsPerLine) {
                    return line.match(new RegExp(`.{1,${maxCharsPerLine}}`, 'g')).join('\n');
                }
                return line;
            });

            const formattedText = lines.join('\n'); // Recria o texto com quebras de linha
            const beforeText = this.value.slice(0, caretPosition); // Texto antes do cursor
            const afterText = this.value.slice(caretPosition); // Texto depois do cursor

            const formattedBeforeText = beforeText.split('\n').map(line => {
                if (line.length > maxCharsPerLine) {
                    return line.match(new RegExp(`.{1,${maxCharsPerLine}}`, 'g')).join('\n');
                }
                return line;
            }).join('\n');

            const newCaretPosition = formattedBeforeText.length; // Nova posição do cursor

            this.value = formattedText;

            this.setSelectionRange(newCaretPosition, newCaretPosition);
        });
    });
});

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
                        // Atualiza contagem de likes
                        likeCountSpan.textContent = data.likes_count;

                        // Atualiza a cor do botão
                        if (data.user_has_liked) {
                            button.classList.add('active'); // Ativa o botão de like
                        } else {
                            button.classList.remove('active'); // Remove a classe se não curtiu
                        }
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
            const commentForm = document.getElementById(`comment-form-${postId}`);

            // Alterna a exibição do formulário de comentários
            if (commentForm.style.display === 'none' || commentForm.style.display === '') {
                commentForm.style.display = 'block';
            } else {
                commentForm.style.display = 'none';
            }
        });
    });
});