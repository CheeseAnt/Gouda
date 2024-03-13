import { Telegram } from "@mui/icons-material";
import Cookies from "js-cookie";
import { useEffect, useState } from "react";
import { Button} from "react-bootstrap";
import { jwtDecode } from "jwt-decode";
import { updateUserTelegramID } from "../api";

const BOT_ID = process.env.REACT_APP_TELEGRAM_BOT_ID ?? "6565603529";
const REDIRECT_URL = process.env.REACT_APP_REDIRECT_URI ?? "http://127.0.0.1:3000"
const AUTH_URL = `https://oauth.telegram.org/auth?bot_id=${BOT_ID}&origin=${REDIRECT_URL}&embed=1&request_access=write&lang=en&return_to=${REDIRECT_URL}`
const TELEGRAM_HASH_COOKIE = 'telelgramHash';

const TelegramAuth = ({jwtInput}) => {
    const [decodedJwt, setDecodedJwt] = useState({});
    
    useEffect(() => {
        if(Object.keys(decodedJwt).length) {
            return;
        }

        var hash;

        if(jwtInput) {
            hash = jwtInput;
        }
        else {
            hash = Cookies.get(TELEGRAM_HASH_COOKIE);
        }

        if(!hash) {
            return;
        }

        const jwtInfo = jwtDecode(hash, { header: true });
        setDecodedJwt(jwtInfo);
    }, [setDecodedJwt]);

    const logOut = () => {
        Cookies.set(TELEGRAM_HASH_COOKIE, '');
        setDecodedJwt({});
        updateUserTelegramID('');
    }

    return <div className="w-100 text-center">
        {
            Object.keys(decodedJwt).length ?
            <div className="d-flex" style={{alignItems: 'center'}}>
                <img className="me-3 rounded-circle thumb-photo" src={decodedJwt.photo_url}/>
                <div className="d-grid">
                    <div>
                        <span className="text-muted">Logged in as: </span>
                        <span>{decodedJwt.first_name} ({decodedJwt.username})</span>
                    </div>
                    <span className="text-muted">{decodedJwt.id}</span>
                    <Button className='telegram btn m-2' onClick={logOut}><Telegram /> Log Out</Button>
                </div>
            </div>
            :
            <Button className='telegram btn m-2' href={AUTH_URL}><Telegram /> Log in with Telegram to receive Notifications</Button>
    }
    </div>
}

var getHash = function getHash() {
    return window ? window.location.hash.substring(1).split('&').reduce(function (initial, item) {
      if (item) {
        var parts = item.split('=');
        initial[parts[0]] = decodeURIComponent(parts[1]);
      }
  
      return initial;
    }, {}) : '';
  };

const useTelegramAuthResponse = () => {
    useEffect(() => {
        const hash = getHash();

        if(hash.tgAuthResult) {
            Cookies.set(TELEGRAM_HASH_COOKIE, hash.tgAuthResult);
            updateUserTelegramID(hash.tgAuthResult);
            document.location.hash = "";
        }
    }, []);
}


export { TelegramAuth, useTelegramAuthResponse };
