const srn=document.querySelector('.srn').innerHTML;
const subtotal = document.querySelectorAll('.price');
const sbdisplay = document.querySelector('.foodsum');
const gstdisplay = document.querySelector('.gst');
const gtdisplay = document.querySelector('.grandtotal');

document.addEventListener('DOMContentLoaded', function() {
    const countButtons = document.querySelectorAll('.addd');
    const subtractButtons = document.querySelectorAll('.sub');
    const countDisplay = document.querySelectorAll('.countc');
    const food = document.querySelectorAll('.food');
    const price = document.querySelectorAll('.price');

    countButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            const count = Number(countDisplay[index].innerHTML);
            countDisplay[index].innerHTML = String(count + 1);
            const selectedFood = food[index].innerHTML;
            const foodPrice = Number(price[index].innerHTML.replace('\u20b9',''));
            var sqlAdd = [selectedFood, foodPrice, count+1, srn];
            let subprice=0
            subtotal.forEach((pr) => {
                subprice+=Number(pr.innerHTML.replace('\u20b9',''))*(count+1);
            });
            gst=Math.round(.18*subprice+4);
            grandtotal=gst+subprice;
            sbdisplay.innerHTML =  '\u20b9'+subprice;
            gstdisplay.innerHTML = '\u20b9'+gst;
            gtdisplay.innerHTML = '\u20b9'+grandtotal;
            fetch('/cartAdd', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sqlAdd)
            })
        });
    });
    let subprice=0
    subtotal.forEach((pr,index) => {
        const count = Number(countDisplay[index].innerHTML);
        subprice+=Number(pr.innerHTML.replace('\u20b9',''))*count;
    });
    let gst=Math.round(.18*subprice+4);
    let grandtotal=gst+subprice;
    sbdisplay.innerHTML =  '\u20b9'+subprice;
    gstdisplay.innerHTML = '\u20b9'+gst;
    gtdisplay.innerHTML = '\u20b9'+grandtotal;


    subtractButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            const count = Number(countDisplay[index].innerHTML);
            const selectedFood = food[index].innerHTML;
            const foodPrice = Number(price[index].innerHTML.replace('\u20b9',''));
            var sqlSub = [selectedFood, foodPrice, count-1, srn];
            var table = document.querySelector('foodtable');
            let subprice=0
            subtotal.forEach((pr) => {
                subprice+=Number(pr.innerHTML.replace('\u20b9',''))*(count-1);
            });
            gst=Math.round(.18*subprice+4);
            grandtotal=gst+subprice;
            sbdisplay.innerHTML =  '\u20b9'+subprice;
            gstdisplay.innerHTML = '\u20b9'+gst;
            gtdisplay.innerHTML = '\u20b9'+grandtotal;
            if (count >= 0) {
                countDisplay[index].innerHTML = String(count - 1);
                if (count==1) {
                    removeTableRow(button);
                    if (table.rows.length==0) {
                        goHome();
                    }
                }
            fetch('/cartSub', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sqlSub)
            })
        }
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

function removeTableRow(button) {
    var row = button.closest('tr');
    row.remove();
    const cartRows = document.querySelectorAll('.cart table tr');
    if (cartRows.length === 1) { 
        window.location.href = '/home';
    }
}

function goHome() {
    fetch('/home', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
}
