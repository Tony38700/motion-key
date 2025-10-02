const API_URL = 'http://127.0.0.1:8000';
let currentUser = null;

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
        'developmentScreen',
        'newUserScreen',
        'firstUserScreen',
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

        showMessage('messageArea', '✅ Login realizado com sucesso!');
        setTimeout(() => showScreen('mainMenu'), 1500);
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
        const res = await fetch(`${API_URL}/users/${currentUser.id}`);
        if (!res.ok) throw new Error('Erro ao buscar dados do usuário');
        const user = await res.json();
        currentUser = normalizeUser(user);

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
        const res = await fetch(`${API_URL}/users/${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                birth,
                phone,
                address,
                email,
                password,
            }),
        });

        if (!res.ok) throw new Error('Erro ao atualizar perfil');
        const updated = await res.json();
        currentUser = normalizeUser(updated);

        showMessage(
            'editProfileMessageArea',
            '✅ Perfil atualizado com sucesso!'
        );
        setTimeout(() => showMainMenu(), 2000);
    } catch (err) {
        showMessage('editProfileMessageArea', err.message, true);
    }
}

function closeFirstUserModal() {
    document.getElementById('firstUserModal').classList.remove('show');
}

function proceedToFirstUser() {
    closeFirstUserModal();
    showScreen('firstUserScreen');
}

async function createFirstUser() {
    const data = {
        name: document.getElementById('firstUserName').value,
        birth: document.getElementById('firstUserBirth').value,
        cpf: document.getElementById('firstUserCPF').value,
        phone: document.getElementById('firstUserPhone').value,
        address: document.getElementById('firstUserAddress').value,
        email: document.getElementById('firstUserEmail').value,
        login: document.getElementById('firstUserLogin').value,
        password: document.getElementById('firstUserPassword').value,
    };
    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!res.ok) throw new Error('Erro ao cadastrar primeiro usuário');

        const user = await res.json();
        currentUser = normalizeUser(user);

        showMessage('firstUserMessageArea', 'Usuário cadastrado com sucesso!');
        showLoginScreen();
    } catch (err) {
        showMessage('firstUserMessageArea', err.message, true);
    }
}

async function createNewUser() {
    const data = {
        name: document.getElementById('newUserName').value,
        birth: document.getElementById('newUserBirth').value,
        cpf: document.getElementById('newUserCPF').value,
        phone: document.getElementById('newUserPhone').value,
        address: document.getElementById('newUserAddress').value,
        email: document.getElementById('newUserEmail').value,
        login: document.getElementById('newUserLogin').value,
        password: document.getElementById('newUserPassword').value,
    };
    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!res.ok) throw new Error('Erro ao cadastrar usuário');

        const user = await res.json();
        currentUser = normalizeUser(user);

        showMessage('newUserMessageArea', 'Usuário cadastrado com sucesso!');
        showMainMenu();
    } catch (err) {
        showMessage('newUserMessageArea', err.message, true);
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
    showScreen('mainMenu');
    const deleteBtn = document.getElementById('deleteUserBtn');
    if (currentUser && currentUser.isAdmin) {
        deleteBtn.style.display = 'block';
    } else {
        deleteBtn.style.display = 'none';
    }
}

function showSelfRegistration() {
    showScreen('selfRegistrationScreen');
}

function showDeleteUserMenu() {
    if (!currentUser || !currentUser.isAdmin) {
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

function showNewUserForm() {
    showScreen('newUserScreen');
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

    try {
        const res = await fetch(`${API_URL}/run-motionkey`, {
            method: 'POST',
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao executar MotionKey');
        }

        const data = await res.json();
        document.getElementById(
            'developmentMessage'
        ).innerText = `✅ MotionKey executado com sucesso!\n${data.output}`;
    } catch (err) {
        document.getElementById(
            'developmentMessage'
        ).innerText = `❌ ${err.message}`;
    }
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
            item.innerHTML = `<div class="user-info"><div class="user-name">${user.name}</div><div class="user-login">${user.login}</div></div>
                              <button class="delete-btn" onclick="deleteUser('${user.login}')">Deletar</button>`;
            listDiv.appendChild(item);
        });
    } catch (err) {
        showMessage('deleteUserMessageArea', err.message, true);
    }
}

async function deleteUser(login) {
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

        const resDelete = await fetch(`${API_URL}/users/${user.id}`, {
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
});
