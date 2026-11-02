function fail(status,message){const e=new Error(message);e.status=status;throw e;}
function text(x,name,max=150){if(typeof x!=='string'||!x.trim()||x.trim().length>max)fail(400,`${name} is required (max ${max} characters).`);return x.trim();}
function integer(x,name,min=1,max=2147483647){const n=Number(x);if(!Number.isSafeInteger(n)||n<min||n>max)fail(400,`Invalid ${name}.`);return n;}
function email(x){const s=text(x,'Email',254).toLowerCase();if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s))fail(400,'Invalid email.');return s;}
function password(x){if(typeof x!=='string'||x.length<8||Buffer.byteLength(x)>72)fail(400,'Password must be 8+ characters, up to 72 UTF-8 bytes.');return x;}
function date(x){if(typeof x!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(x))fail(400,'Use a UTC date, e.g. 2027-06-10T05:00:00Z.');const d=new Date(x);if(Number(x.slice(0,4))<1000||!Number.isFinite(d.getTime())||d.toISOString().replace('.000','')!==x)fail(400,'Invalid date.');return d.toISOString().slice(0,19).replace('T',' ');}
module.exports={fail,text,integer,email,password,date};
