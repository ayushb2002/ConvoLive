document.addEventListener('DOMContentLoaded', ()=>{

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    window.addEventListener('load', ()=>{
        window.scrollTo(0, document.body.scrollHeight);
        myfun();
    });


    socket.on('connect', () => {
        document.querySelector('#sendmsg').onclick = () => {
            var pname = document.querySelector('#pname').value;
            var room = document.querySelector('#room').value;
            var d = document.querySelector('#messarea').value;
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
            var yyyy = today.getFullYear();
            var min = (today.getMinutes()<10?'0':'') + today.getMinutes();
            var t = today.getHours()+':'+min;
            today = mm + '/' + dd + '/' + yyyy;
            //alert(pname+" "+room+" "+d);
            if(d == "")
            return -1;
            else
            {
            var msg = pname+'- '+d;
            var timest = '( Sent on '+today+' at:'+t+' )';
            document.querySelector('#messarea').value = ""
            socket.emit('sendmsg', {'msg': msg, 'room': room, 'name': pname, 'time': timest});
            }
        };

        document.querySelectorAll('.todel').forEach(button => {    
            button.onclick = () => {
            n = button.dataset.name;
            sid = 'i'+button.dataset.id;
            lid = 'l'+button.dataset.id;
            name = document.querySelector('#pname').value;
            //alert('clicked!');
            if(name == n){
                var e = document.getElementById(lid);
                var s = document.getElementById(sid).innerHTML;
                //alert(s+'\n'+e);
                var room = document.querySelector('#room').value;
                e.style.animationPlayState = 'running';
                e.addEventListener('animationend', () =>{
                   //alert('click');
                    e.parentElement.remove();
                    socket.emit('delmsg', {'mess': s, 'room': room, 'name': name})
                });
            }
            else
            button.display = 'none';
            }        
        });

    });

    var i = 0;

    socket.on('loadmsg', data => {
        var name = `${data.name}`;
        var name2 = document.querySelector('#pname').value;
        var room = document.querySelector('#room').value;
        var r = `${data.room}`;
        //alert(r);
        if (room == r)
        {
        var li = document.createElement('li');
        var st =  `${data.mess}`;
        li.style.padding = '2%';
        var span = document.createElement('span');
        span.innerHTML = st;
        span.classList.add('float-left');
        span.id = '0'+i;

        var button = document.createElement('button');
        button.innerHTML = "DELETE";
        button.classList.add('btn');
        button.classList.add('btn-success');
        button.classList.add('float-right');
        button.id= i;
        button.setAttribute('data-id', i);
        button.style.display = 'block';
        i++;
        button.addEventListener('click',  ()=>{
            if (name == name2){
            var id1 = button.dataset.id;
            var id = '0'+id1;
            var e = document.getElementById(id1);
            e.parentElement.style.animationPlayState = 'running';
            var s = document.getElementById(id).innerHTML;
            e.parentElement.addEventListener('animationend', () =>{
            e.parentElement.remove();
            socket.emit('delmsg', {'mess': s, 'room': room, 'name': pname})
        });
            } 
            else
            button.style.display = 'none';
        });

            li.appendChild(span);
            li.appendChild(button);
    
            document.querySelector('#messages').append(li);
        }
        
    });

    socket.on('successmsg', data => {
        location.reload();
        console.log(`${data.msg}`);
        
    });



});


window.onscroll= function(){
    if(window.scrollY == 0)
    {
        var n = document.getElementById('messages').getElementsByTagName('li').length;
        if (n>100)
        for(var x=100;x<n;x++)
        {
        var id = 'l'+x.toString();
        var e = document.getElementById(id);
        setTimeout(function(){e.style.display = 'block';}, 2000)
        }
    }
}

function myfun()
{
    var n = document.getElementById('messages').getElementsByTagName('li').length;
    //alert(n);
    if(n<100)
    {
        console.log('working on it!');
    }
    else
    {
        for(var x=100;x<n;x++)
        {
        var id = 'l'+x.toString();
        var e = document.getElementById(id);
        e.style.display = 'none';
        }
    }
}