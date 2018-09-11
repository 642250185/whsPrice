var request = require('request');
var md5     = require("md5");
var fs      = require('fs');
var xlsx    = require('node-xlsx').default;
var obj     = xlsx.parse('./whs.xlsx');
const execa = require('execa');

const config = require('./config');
if(config.autoGetCookie) {
	try{
		execa.shellSync('python cookie.py', {
			cwd: './cookie',
			stdio: 'inherit'
		});
	}catch (e) {
		console.log(e);
		return;
	}
}

var cookie  = fs.readFileSync('./cookie/cookie.txt', 'utf-8').trim().split('\r\n');

function getList(){

    var list = obj[0].data.concat();
    list.shift();
    list.len = list.length;
    return list;
}


function hsb(list, next){

    var item = list.shift();

    if (!item){
        return !list.len && next(getList());
    }

    var data    = {
        "mid"     : '' + item[2],
        "pid"     : "1114",
        "selects" : '' + item[3],
        "time"    : '' + (+new Date / 1000 >> 0)
    }

    var sign = [];

    sign.push('mid='       + data.mid);
    sign.push('pid='       + data.pid);
    sign.push('selects='   + data.selects);
    sign.push('time='      + data.time);
    sign.push('key='       + '1f3870be274f6c49b3e31a0c6728957f');
    sign        = sign.join('&');
    data.sign   = md5(sign);
    // console.log(data);

    request.post({

        url    : 'http://openapi.huishoubao.com/qq/evaluate',
        body   : data,
        json   : true

    }, function(err, res, json){

        console.log(json.errcode, json.price / 100 >> 0, --list.len);
        item.push(+json.price / 100 >> 0);
        hsb(list, next);
    });
}

function end(){
    fs.writeFileSync('./cookie/cookie.txt', cookie.join('\r\n'));
    fs.writeFileSync('./whs2.xlsx', xlsx.build(obj));
}



function requestWHS(mid, selects, list, callback){

    var ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1';
    var ck = cookie.shift();

    if (!ck){
        return end();
    }
    request.post({
        url   : 'https://chong.qq.com/tws/recycleevaluate/GetEvaluateResult',
        qs    : {
            appId   : 'wx47031447c8352579',
            UidType : '1',
            vb2ctag : 'PC_sq',
        },
        json   : true,
        body : {
            mid     : '' + mid,
            selects : '' + selects,
            time    : +new Date,
        },
        headers: {
            'User-Agent': ua,
            'Cookie'    : ck,
        }
    }, function (err, res, json){

        if (err) {
            cookie.unshift(ck);
            console.log('requestWHS.err');
            return requestWHS(mid, selects, list, callback);
        }
        if (+json.errcode){
            console.log('requestWHS.json.errcode', json);
            return requestWHS(mid, selects, list, callback)
        }
        console.log(err, +json.errcode, +json.data.price / 100 >> 0, --list.len, ck);
        cookie.push(ck);
        callback(json);
    });
}


function whs (list){

    var item = list.shift();

    if (!item){
        console.log('---------------------');
        return !list.len && end();
    }

    requestWHS(item[2], item[3], list, function(json){
        var pirce = +json.data.price / 100 >> 0
        item.push(pirce, item[4]-pirce);
        // console.log(item);
        setTimeout(whs, 1000 / cookie.length, list);
    })
}

// try {
	// fs.unlinkSync('./whs2.xlsx');
// }catch(e) {
	
// }finally {
	
// }
var list = getList();
	hsb(list, whs);

