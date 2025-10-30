const API_URL = 'http://127.0.0.1:8000';

function showMessage(containerId, message, isError = false) {
    const container = document.getElementById(containerId);
    const messageClass = isError ? 'error-message' : 'success-message';
    container.innerHTML = `<div class="${messageClass}">${message}</div>`;
    setTimeout(() => (container.innerHTML = ''), 5000);
}

function showScreen(screenId) {
    const screens = [
        'selfRegistrationScreen',
        'loginScreen',
        'mainMenu',
        'editProfileScreen',
        'deleteUserScreen',
        'manualScreen',
        'developmentScreen',
    ];
    screens.forEach((screen) => {
        const el = document.getElementById(screen);
        if (el) el.classList.add('hidden');
    });
    const target = document.getElementById(screenId);
    if (target) target.classList.remove('hidden');
}

function isValidCPF(cpf) {
    return /^\d{11}$/.test(cpf);
}

function isValidPhone(phone) {
    return /^\d{10,11}$/.test(phone);
}

function isValidName(name) {
    return /^[a-zA-ZÀ-ÿ\s]+$/.test(name);
}

function isValidBirthDate(dateStr) {
    if (!dateStr) return false;
    // Expect format YYYY-MM-DD
    const parts = dateStr.split('-');
    if (parts.length !== 3) return false;
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // JS months 0-11
    const day = parseInt(parts[2], 10);
    if (Number.isNaN(year) || Number.isNaN(month) || Number.isNaN(day))
        return false;

    const birth = new Date(year, month, day);
    if (isNaN(birth.getTime())) return false;

    const today = new Date();
    const thisYear = today.getFullYear();

    if (year > thisYear) return false;

    // Compute age accurately
    let age = thisYear - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
        age--;
    }

    if (age < 0 || age > 105) return false;

    return true;
}

function normalizeUser(user) {
    return {
        ...user,
        isAdmin: user.is_admin || false,
    };
}

async function loginUser() {
    const login = document.getElementById('loginInput').value.trim();
    const password = document.getElementById('passwordInput').value.trim();

    if (!login || !password) {
        showMessage(
            'messageArea',
            'Por favor, preencha todos os campos.',
            true
        );
        return;
    }

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, password }),
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData?.message || 'Login ou senha inválidos');
        }

        const user = await res.json();
        currentUser = normalizeUser(user);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showMessage('messageArea', '✅ Login realizado com sucesso!');
        setTimeout(() => showMainMenu(), 1500);
    } catch (err) {
        showMessage('messageArea', 'Login ou senha incorretos.', true);
    }
}

async function showEditProfile() {
    if (!currentUser) {
        showMessage(
            'mainMenuMessageArea',
            'Você precisa estar logado para editar seu perfil.',
            true
        );
        return;
    }

    try {
        const res = await fetch(`${API_URL}/users/${currentUser.id_pessoa}`);
        if (!res.ok) throw new Error('Erro ao buscar dados do usuário');
        const user = await res.json();
        currentUser = normalizeUser(user);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showScreen('editProfileScreen');

        document.getElementById('editProfileName').value = user.name;
        document.getElementById('editProfileBirth').value = user.birth;
        document.getElementById('editProfileCPF').value = user.cpf;
        document.getElementById('editProfilePhone').value = user.phone;
        document.getElementById('editProfileAddress').value = user.address;
        document.getElementById('editProfileEmail').value = user.email;
        document.getElementById('editProfileLogin').value = user.login;
        document.getElementById('editProfilePassword').value = user.password;
    } catch (err) {
        showMessage('mainMenuMessageArea', err.message, true);
    }
}

async function saveProfileEdit() {
    const name = document.getElementById('editProfileName').value.trim();
    const birth = document.getElementById('editProfileBirth').value;
    const phone = document.getElementById('editProfilePhone').value.trim();
    const address = document.getElementById('editProfileAddress').value.trim();
    const email = document.getElementById('editProfileEmail').value.trim();
    const password = document.getElementById('editProfilePassword').value;

    if (!name || !birth || !phone || !address || !password) {
        showMessage(
            'editProfileMessageArea',
            'Preencha todos os campos obrigatórios.',
            true
        );
        return;
    }

    if (!isValidBirthDate(birth)) {
        showMessage(
            'editProfileMessageArea',
            'Data de nascimento inválida. Verifique o ano e a idade (máx 105 anos).',
            true
        );
        return;
    }

    if (!isValidName(name)) {
        showMessage(
            'editProfileMessageArea',
            'Nome deve conter apenas letras e espaços.',
            true
        );
        return;
    }

    if (!isValidPhone(phone)) {
        showMessage(
            'editProfileMessageArea',
            'Telefone deve conter 10 ou 11 números.',
            true
        );
        return;
    }

    try {
        is_admin = currentUser.is_admin;
        const res = await fetch(`${API_URL}/users/${currentUser.id_pessoa}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                birth,
                phone,
                address,
                email,
                password,
                is_admin,
            }),
        });

        if (!res.ok) throw new Error('Erro ao atualizar perfil');
        const updated = await res.json();
        currentUser = normalizeUser(updated);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showMessage(
            'editProfileMessageArea',
            '✅ Perfil atualizado com sucesso!'
        );
        setTimeout(() => showMainMenu(), 2000);
    } catch (err) {
        showMessage('editProfileMessageArea', err.message, true);
    }
}

async function createSelfRegistration() {
    const data = {
        name: document.getElementById('selfRegName').value,
        birth: document.getElementById('selfRegBirth').value,
        cpf: document.getElementById('selfRegCPF').value,
        phone: document.getElementById('selfRegPhone').value,
        address: document.getElementById('selfRegAddress').value,
        email: document.getElementById('selfRegEmail').value,
        login: document.getElementById('selfRegLogin').value,
        password: document.getElementById('selfRegPassword').value,
        admin_code: document.getElementById('selfRegAdminCode')
            ? document.getElementById('selfRegAdminCode').value
            : '',
    };

    if (
        !data.name ||
        !data.birth ||
        !data.cpf ||
        !data.phone ||
        !data.address ||
        !data.login ||
        !data.password
    ) {
        showMessage(
            'selfRegMessageArea',
            'Por favor, preencha todos os campos obrigatórios.',
            true
        );
        return;
    }
    if (!isValidBirthDate(data.birth)) {
        showMessage(
            'selfRegMessageArea',
            'Data de nascimento inválida. Verifique o ano e a idade (máx 105 anos).',
            true
        );
        return;
    }
    if (!isValidName(data.name)) {
        showMessage(
            'selfRegMessageArea',
            'Nome deve conter apenas letras e espaços.',
            true
        );
        return;
    }
    if (!isValidCPF(data.cpf)) {
        showMessage(
            'selfRegMessageArea',
            'CPF deve conter exatamente 11 números.',
            true
        );
        return;
    }
    if (!isValidPhone(data.phone)) {
        showMessage(
            'selfRegMessageArea',
            'Telefone deve conter 10 ou 11 números.',
            true
        );
        return;
    }

    try {
        const res = await fetch(`${API_URL}/self-register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao criar conta.');
        }

        const user = await res.json();
        currentUser = normalizeUser(user);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));

        showMessage(
            'selfRegMessageArea',
            `✅ Conta criada com sucesso!${
                data.admin_code ? ' (Administrador)' : ''
            }`
        );

        // Limpar formulário
        [
            'selfRegName',
            'selfRegBirth',
            'selfRegCPF',
            'selfRegPhone',
            'selfRegAddress',
            'selfRegEmail',
            'selfRegLogin',
            'selfRegPassword',
            'selfRegAdminCode',
        ].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });

        setTimeout(() => {
            showLoginScreen();
            showMessage(
                'messageArea',
                '✅ Conta criada! Faça login para continuar.'
            );
        }, 2000);
    } catch (err) {
        showMessage('selfRegMessageArea', err.message, true);
    }
}

function showLoginScreen() {
    showScreen('loginScreen');
}

function showMainMenu() {
    const userData = localStorage.getItem('currentUser');
    const user = userData ? JSON.parse(userData) : null;

    if (!user) {
        showMessage('mainMenuMessageArea', 'Você precisa estar logado.', true);
        return;
    }

    showScreen('mainMenu');
    const deleteBtn = document.getElementById('deleteUserBtn');
    deleteBtn.style.display = user.is_admin ? 'block' : 'none';
}

function showSelfRegistration() {
    showScreen('selfRegistrationScreen');
}

function showManual() {
    showScreen('manualScreen');
}

function showDeleteUserMenu() {
    const userData = localStorage.getItem('currentUser');
    const user = userData ? JSON.parse(userData) : null;

    if (!user || !user.isAdmin) {
        showMessage(
            'mainMenuMessageArea',
            'Acesso negado. Apenas administradores podem deletar usuários.',
            true
        );
        return;
    }

    showScreen('deleteUserScreen');
    loadUsersList();
}

function logout() {
    currentUser = null;
    document.getElementById('loginInput').value = '';
    document.getElementById('passwordInput').value = '';
    showLoginScreen();
}

function showGestureMenu() {
    document.getElementById('developmentMessage').textContent =
        'Adicionar Gesto - Em desenvolvimento';
    showScreen('developmentScreen');
}

function showRelationMenu() {
    document.getElementById('developmentMessage').textContent =
        'Reorganizar relação gesto/comando - Em desenvolvimento';
    showScreen('developmentScreen');
}

async function runMotionKey() {
    showScreen('developmentScreen');
    document.getElementById('developmentMessage').innerText =
        'Executando MotionKey...';

    const hand = await showHandModal();
    if (!hand) {
        document.getElementById('developmentMessage').innerText =
            'Execução cancelada.';
        return;
    }
    try {
        const currentUser = JSON.parse(
            localStorage.getItem('currentUser') || 'null'
        );
        const res = await fetch(`${API_URL}/run-motionkey`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hand, current_user: currentUser }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao executar MotionKey');
        }

        const data = await res.json();
        document.getElementById('developmentMessage').innerText =
            data.detail || '✅ MotionKey executado.';
    } catch (err) {
        document.getElementById(
            'developmentMessage'
        ).innerText = `❌ ${err.message}`;
    }
}

// --- Modal de seleção de mão (promise-based) ---
function showHandModal() {
    return new Promise((resolve) => {
        const overlay = document.getElementById('handModalOverlay');
        const leftBtn = document.getElementById('handLeftBtn');
        const rightBtn = document.getElementById('handRightBtn');
        const cancelBtn = document.getElementById('handCancelBtn');

        if (!overlay || !leftBtn || !rightBtn || !cancelBtn) {
            // fallback para prompt se modal não estiver presente
            const fallback = prompt(
                'Você é canhoto ou destro? Digite "left" ou "right".',
                'right'
            );
            resolve(
                fallback && fallback.toLowerCase() === 'left' ? 'left' : 'right'
            );
            return;
        }

        function cleanup() {
            overlay.classList.remove('show');
            leftBtn.removeEventListener('click', onLeft);
            rightBtn.removeEventListener('click', onRight);
            cancelBtn.removeEventListener('click', onCancel);
        }

        function onLeft() {
            cleanup();
            resolve('left');
        }
        function onRight() {
            cleanup();
            resolve('right');
        }
        function onCancel() {
            cleanup();
            resolve(null);
        }

        leftBtn.addEventListener('click', onLeft);
        rightBtn.addEventListener('click', onRight);
        cancelBtn.addEventListener('click', onCancel);

        // show modal
        overlay.classList.add('show');
    });
}

async function loadUsersList() {
    const listDiv = document.getElementById('usersList');
    if (!listDiv) return;
    try {
        const res = await fetch(`${API_URL}/users`);
        if (!res.ok) throw new Error('Erro ao carregar usuários');
        const users = await res.json();
        listDiv.innerHTML = '';
        users.forEach((u) => {
            const user = normalizeUser(u);
            const item = document.createElement('div');
            item.className = 'user-item';
            item.innerHTML = `<div class="user-info"><div class="user-name">${
                user.name
            } ${user.isAdmin ? '👑' : ''}</div><div class="user-login">${
                user.login
            }</div></div>
                              <button class="delete-btn" onclick="deleteUser('${
                                  user.login
                              }')">Deletar</button>`;
            listDiv.appendChild(item);
        });
    } catch (err) {
        showMessage('deleteUserMessageArea', err.message, true);
    }
}

async function deleteUser(login) {
    const userData = localStorage.getItem('currentUser');
    const currentUser = userData ? JSON.parse(userData) : null;

    if (!currentUser || !currentUser.isAdmin) {
        showMessage(
            'deleteUserMessageArea',
            'Acesso negado. Apenas administradores podem deletar usuários.',
            true
        );
        return;
    }

    if (currentUser.login === login) {
        showMessage(
            'deleteUserMessageArea',
            'Você não pode deletar sua própria conta.',
            true
        );
        return;
    }

    if (!confirm(`Tem certeza que deseja deletar o usuário "${login}"?`)) {
        return;
    }

    try {
        const resUsers = await fetch(`${API_URL}/users`);
        const allUsers = await resUsers.json();
        const user = allUsers.find((u) => u.login === login);

        if (!user) {
            showMessage(
                'deleteUserMessageArea',
                `Usuário "${login}" não encontrado.`,
                true
            );
            return;
        }

        const resDelete = await fetch(`${API_URL}/users/${user.id_pessoa}`, {
            method: 'DELETE',
        });

        if (!resDelete.ok) {
            const err = await resDelete.json();
            throw new Error(err.detail || 'Erro ao deletar usuário.');
        }

        showMessage(
            'deleteUserMessageArea',
            `✅ Usuário "${login}" deletado com sucesso!`
        );
        loadUsersList();
    } catch (err) {
        showMessage('deleteUserMessageArea', err.message, true);
    }
}

// Eventos de teclado para login
document.addEventListener('DOMContentLoaded', function () {
    showScreen('loginScreen');
    if (document.getElementById('loginInput')) {
        document
            .getElementById('loginInput')
            .addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    document.getElementById('passwordInput').focus();
                }
            });
        document
            .getElementById('passwordInput')
            .addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    loginUser();
                }
            });
    }

    // Configuração dos inputs de data para limitar seleção: mínimo = hoje - 105 anos, máximo = hoje
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const maxDate = `${yyyy}-${mm}-${dd}`;
    const minDate = `${yyyy - 105}-${mm}-${dd}`;
    const birthInputs = [
        document.getElementById('selfRegBirth'),
        document.getElementById('editProfileBirth'),
    ];
    birthInputs.forEach((input) => {
        if (input) {
            input.setAttribute('max', maxDate);
            input.setAttribute('min', minDate);
        }
    });
});
