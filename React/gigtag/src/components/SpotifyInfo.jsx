import { useCallback, useEffect, useState } from 'react';
import { getUserInfo, refreshUserPlaylists, getUserPlaylists, togglePlaylist } from '../api'
import { Loader } from './Loader';

const SpotifyUserInfo = ( {setInvalid, children} ) => {
    const [userInfo, setUserInfo] = useState({});

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

        setUserInfo(json);
    }, [setInvalid, setUserInfo]);

    useEffect(() => {
        getUser();
    }, [getUser]);

    return <div className='d-grid' style={{justifyItems: 'center'}}>
        <div className='d-flex user-info' style={{justifyContent: 'space-between'}}>
            <div className='d-flex' style={{alignItems: 'center'}}>
                <img className='me-3 rounded-circle' alt='Profile' style={{width: "64px", height: "64px"}} src={userInfo.photo_url} />
                <h1 className='fw-bold mx-2'>{userInfo.name}</h1>
                <div className='d-grid mx-2'>
                    <span className='text-muted'>Playlists: {userInfo.playlists}</span>
                    <span className='text-muted'>Artists: {userInfo.artists}</span>
                </div>
            </div>
            <div className='spot-tabs mx-3 d-flex'>
                {children.map(c => 
                    <button 
                        key={c.props.name}
                        className={(c.props.name===tab ? 'active ': '') + 'btn btn-secondary mx-1'}
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
            setLoading(false);
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
            loading ? <Loader /> :
            <div className='container'>
                <button className='btn btn-info px-10 w-100' onClick={refreshPlaylists}>Refresh from Spotify</button>
                <h4 className="text-muted">Total Playlists: {Object.keys(playlists).length}</h4>
                {Object.values(playlists).map(playlist => {
                    return <div key={playlist.id} className='playlist d-flex'>
                        <img className='me-3' alt='Playlist' style={{width: "64px"}} src={playlist.image_url} />
                        <div className='d-flex w-100' style={{justifyContent: 'space-between'}}>
                            <div>
                                <h1 className='fw-bold mx-3'>{playlist.name}</h1>
                                <h3 className='mx-3 text-muted'>{playlist.last_updated}</h3>
                                <div className='d-flex'>
                                    <h3 className='mx-3 text-muted'>Tracks: {playlist.track_count}</h3>
                                    <h3 className='mx-3 text-muted'>{playlist.public ? 'Public' : 'Private'}</h3>
                                    <h3 className='mx-3 text-muted'>{playlist.owner}</h3>
                                </div>
                            </div>
                            <button className='btn btn-info m-3 px-4' style={{fontSize: 'xxx-large'}} data-mdb-toggle="button" onClick={() => togglePl(playlist)}>
                                {playlist.enabled ? '☑' : '☐'}
                            </button>
                        </div>
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
