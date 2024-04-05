const indicator = document.querySelector('.nav-indicator');
const items = document.querySelectorAll('.nav-item');
const menu = document.querySelector('#Menu');
const wall = document.querySelector('#Wallet');
const support = document.querySelector('#Support');
const orders = document.querySelector('#Orders');
const srn = document.querySelector('.srn').innerHTML;

function closeAll() {
    menu.style.display = 'none';
    wall.style.display = 'none';
    support.style.display = 'none';
    orders.style.display = 'none';
}

function openMenu() {
    menu.style.display = 'grid';
}

function handleIndicator(el) {
    items.forEach(item => {
        item.classList.remove('is-active');
        item.removeAttribute('style');
    });
    
    indicator.style.width = `${el.offsetWidth}px`;
    indicator.style.left = `${el.offsetLeft}px`;
    indicator.style.backgroundColor = el.getAttribute('active-color');

    el.classList.add('is-active');
    el.style.color = el.getAttribute('active-color');
}

items.forEach((item) => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        handleIndicator(e.target);
    });
    item.classList.contains('is-active') && handleIndicator(item);
});

document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeAll();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetId=='#Menu') {
                targetSection.style.display = 'grid';
            }
            else {
                targetSection.style.display = 'flex';
            }
        });
    });
    const countButtons = document.querySelectorAll('.addd');
    const subtractButtons = document.querySelectorAll('.sub');
    const countDisplay = document.querySelectorAll('.countc');
    const food = document.querySelectorAll('.food');
    const price = document.querySelectorAll('.price');
    const checkoutDisplay = document.querySelector('.chkt');

    countButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            const count = Number(countDisplay[index].innerHTML);
            countDisplay[index].innerHTML = String(count + 1);
            const selectedFood = food[index].innerHTML;
            const foodPrice = Number(price[index].innerHTML.replace('\u20b9',''));
            var sqlAdd = [selectedFood, foodPrice, count+1, srn];
            fetch('/cartAdd', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sqlAdd)
            })
            .then(response => response.text())
            .catch(error => console.error('Error:', error));
            cdisplay(countDisplay,checkoutDisplay);
        });
    });

    subtractButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            const count = Number(countDisplay[index].innerHTML);
            const selectedFood = food[index].innerHTML;
            const foodPrice = Number(price[index].innerHTML.replace('\u20b9',''));
            var sqlSub = [selectedFood, foodPrice, count-1, srn];
            if (count > 0) {
                countDisplay[index].innerHTML = String(count - 1);
            }
            fetch('/cartSub', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sqlSub)
            })
            .then(response => response.text())
            .catch(error => console.error('Error:', error));
            cdisplay(countDisplay,checkoutDisplay);
            
        });
    });

    const propop = document.querySelector('.pfp');
    const prodisplay = document.querySelector('.propop');
    propop.addEventListener('click', () => {
        if (prodisplay.style.display == 'none') {
            prodisplay.style.display = 'flex';
        }
        else {
            prodisplay.style.display = 'none';
        }
    });
});

function cdisplay(y,checkoutDisplay) {
    let chkitems='';
    let nitems=y.length;
    s='';
    for(let i=0;i<nitems;i++) {
        s+='0';
    }
    y.forEach((p,index) => {
        chkitems+=y[index].innerHTML;
    });
    if (chkitems!=s) {
        checkoutDisplay.style.display='flex';
    }
    else {
        checkoutDisplay.style.display='none';
    }
}



