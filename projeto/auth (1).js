// --- AUTH SCRIPT (CONECTADO AO PYTHONANYWHERE) ---

// Define o endereço do seu servidor oficial na nuvem
const API_URL = 'https://jaozinpagod.pythonanywhere.com';
window.API_URL = API_URL; // Deixa global para as outras páginas usarem

const token = sessionStorage.getItem('token');
const userRole = sessionStorage.getItem('userRole');
const forceLogoutData = JSON.parse(localStorage.getItem('forceLogout'));

// 1. Definição das permissões de cada perfil
const permissions = {
    'CEO': ['dashboard.html', 'alunos.html', 'presenca.html', 'aulas.html', 'vendas.html', 'financas.html', 'usuarios.html', 'configuracoes.html'],
    'Administrador': ['dashboard.html', 'alunos.html', 'presenca.html', 'aulas.html', 'vendas.html', 'financas.html', 'usuarios.html', 'configuracoes.html'],
    'Professor': ['alunos.html', 'presenca.html', 'aulas.html'],
    'Vendedor': ['vendas.html']
};

// 2. Verificação de Segurança (Agora checa o Token do servidor)
if (!token) {
    if (!window.location.pathname.endsWith('index.html') && !window.location.pathname.endsWith('login.html') && window.location.pathname !== '/') {
         window.location.href = 'index.html';
    }
} else {
    // Verifica permissões
    const userPermissions = permissions[userRole] || [];
    const currentPage = window.location.pathname.split('/').pop();
    
    // Se a página não é o login/index, verifica se tem acesso
    if (currentPage !== 'index.html' && currentPage !== 'login.html') {
        if (userPermissions.length > 0 && !userPermissions.includes(currentPage)) {
            window.location.href = userPermissions[0];
        }
    }
}

// 3. Estrutura do menu
const menuItems = [
    { name: 'Início', href: 'dashboard.html', icon: 'ph-house' },
    { name: 'Alunos', href: 'alunos.html', icon: 'ph-users' },
    { name: 'Presença', href: 'presenca.html', icon: 'ph-check-square' },
    { name: 'Aulas do Dia', href: 'aulas.html', icon: 'ph-chalkboard-teacher' },
    { name: 'Vendas', href: 'vendas.html', icon: 'ph-shopping-cart' },
    { name: 'Finanças', href: 'financas.html', icon: 'ph-currency-circle-dollar' },
    { name: 'Usuários', href: 'usuarios.html', icon: 'ph-user-gear' },
    { name: 'Configurações', href: 'configuracoes.html', icon: 'ph-gear' }
];

// 4. Função para gerar o menu lateral
function generateSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar || !token) return;

    const userPermissions = permissions[userRole] || [];
    const currentPage = window.location.pathname.split('/').pop();

    let menuHtml = `
        <div class="sidebar-header">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNV8dxYF7dGp6TSUvr5KLLddCultBUPuo8XA&s" alt="Logo Arena Louzada">
            <h2>ARENA LOUZADA</h2>
            <p style="color: var(--text-muted); margin-top: 5px;">(${userRole})</p>
        </div>
        <nav class="nav-menu">
    `;

    menuItems.forEach(item => {
        if (userPermissions.includes(item.href)) {
            const isActive = currentPage === item.href ? 'active' : '';
            menuHtml += `<a href="${item.href}" class="${isActive}"><i class="ph-fill ${item.icon}"></i> <span>${item.name}</span></a>`;
        }
    });
    
    menuHtml += `</nav><a href="#" id="logout-btn" style="text-decoration:none; color: var(--text-muted); text-align:center; padding:10px; font-weight:bold;">Sair</a>`;
    sidebar.innerHTML = menuHtml;
    
    document.getElementById('logout-btn').addEventListener('click', () => {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('userRole');
        window.location.href = 'index.html'; // Garante que volta para a tela inicial
    });
}

document.addEventListener('DOMContentLoaded', generateSidebar);
