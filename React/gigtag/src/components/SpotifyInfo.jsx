import { useCallback, useEffect, useState } from 'react';
import { getUserInfo, refreshUserPlaylists, getUserPlaylists, togglePlaylist } from '../api'
import { Spinner } from 'react-bootstrap'

const SpotifyUserInfo = ( {setInvalid, children} ) => {
    const [name, setName] = useState("");
    const [id, setID] = useState("");
    const [image, setImage] = useState("");

    if(!(children instanceof Array)) {
        children = [children];
    }

    const [tab, setTab] = useState(children[0].props.name);

    const getUser = useCallback(async () => {
        const res = await getUserInfo();
        if(!res.ok) {
            setInvalid(true);
            return;
        }

        const json = await res.json();
        
        setName(json.name);
        setID(json.id);
        setImage(json.photo_url);
    }, [setInvalid, setName, setID, setImage]);

    useEffect(() => {
        getUser();
    }, [getUser]);

    return <div>
        <div className='d-flex user-info' style={{justifyContent: 'space-between'}}>
            <div className='d-flex'>
                <img className='me-3 rounded-circle' alt='Profile' style={{width: "64px"}} src={image} />
                <h1 className='fw-bold mx-2'>{name}</h1>
                <h3 className='text-muted mx-3'>{id}</h3>
            </div>
            <div className='spot-tabs mx-3 d-flex'>
                {children.map(c => 
                    <button 
                        key={c.props.name}
                        className='btn btn-secondary mx-1'
                        onClick={() => setTab(c.props.name)}>
                            {c.props.name}
                    </button>
                )}
            </div>
        </div>
        <div>
            {children.map(child => <div key={child.props.name} style={{display: child.props.name === tab ? 'block': 'none'}}>{child}</div>)}
        </div>
    </div>
}

const SpotifyPlaylists = () => {
    const [ playlists, setPlaylists ] = useState({});
    const [loading, setLoading] = useState(false);

    const refreshPlaylists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);

        const res = await refreshUserPlaylists();
        if(!res.ok) {
            console.log("Error loading playlists: ", res)
            return;
        }
        const json = await res.json();

        setPlaylists(json);

        setLoading(false);
    }, [loading, setLoading, setPlaylists]);

    const getPlaylists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);

        const res = await getUserPlaylists();
        if(!res.ok) {
            console.log("Error loading playlists: ", res)
            return;
        }
        const json = await res.json();

        setPlaylists(json);
        setLoading(false);

        return Object.keys(json).length;
    }, [loading, setLoading, setPlaylists]);

    useEffect(() => {
        if(Object.keys(playlists).length) {
            return;
        }

        getPlaylists().then((res) => {
            if (!res) {
                refreshPlaylists();
            }
        })
    }, [getPlaylists, refreshPlaylists, playlists]);

    const togglePl = useCallback((playlist) => {
        togglePlaylist(playlist.id, !playlist.enabled);
        setPlaylists((previous) => ({
            ...previous,
            [playlist.id]: {
                ...previous[playlist.id],
                enabled: !previous[playlist.id].enabled,
            },
        }));
    }, [setPlaylists]);

    return <div>
        {
            loading ? <Spinner></Spinner> :
            <div className='container'>
                <button className='btn btn-info px-10 w-100' onClick={refreshPlaylists}>Refresh from Spotify</button>
                {Object.values(playlists).map(playlist => {
                    return <div key={playlist.id} className='playlist d-flex' style={{justifyContent: 'space-between'}}>
                        <div>
                            <h1 className='fw-bold mx-3'>{playlist.name}</h1>
                            <div className='d-flex'>
                                <h3 className='mx-3 text-muted'>{playlist.track_count}</h3>
                                <h3 className='mx-3 text-muted'>{playlist.id}</h3>
                                <h3 className='mx-3 text-muted'>{playlist.owner}</h3>
                            </div>
                        </div>
                        <button className='btn btn-info m-3 px-4' style={{fontSize: 'xxx-large'}} data-mdb-toggle="button" onClick={() => togglePl(playlist)}>
                            {playlist.enabled ? '☑' : '☐'}
                        </button>
                    </div>
                })}
            </div>
        }
    </div>
}

const SpotifyInfo = ({setInvalid}) => {
    return (
        <div className='container'>
            <SpotifyPlaylists />
        </div>
    )
}

export { SpotifyInfo, SpotifyUserInfo }
