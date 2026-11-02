const mysql=require('mysql2/promise');
module.exports=mysql.createPool({host:process.env.DB_HOST||'127.0.0.1',port:Number(process.env.DB_PORT||3306),user:process.env.DB_USER||'campusos',password:process.env.DB_PASSWORD||'',database:process.env.DB_NAME||'campusos_v2',connectionLimit:10,dateStrings:true,timezone:'Z',decimalNumbers:true});
