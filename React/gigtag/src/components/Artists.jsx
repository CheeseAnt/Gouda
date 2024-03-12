import { useCallback, useEffect, useState } from "react";
import { getuserArtists, refreshUserArtists } from "../api";
import { Loader } from "./Loader";
import { toggleArtist } from "../api";

const useArtists = () => {
    const [artists, setArtists] = useState([]);
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);

    const getArtists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);
        const res = await getuserArtists();

        if(!res.ok) {
            setLoading(false);
            console.log("Failed to fetch user artists", res)
            return;
        }

        setArtists(await res.json());
        setLoading(false);
        setDone(true);
    }, [loading, setArtists, setLoading]);

    const refreshArtists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);
        const res = await refreshUserArtists();

        if(!res.ok) {
            setLoading(false);
            console.log("Failed to fetch user artists", res)
            return;
        }

        setArtists(await res.json());
        setLoading(false);
    }, [loading, setArtists, setLoading]);

    const toggleAr = useCallback(async (artist) => {
        toggleArtist(artist.name, !artist.enabled);
        setArtists((previous) => ({
            ...previous,
            [artist.name]: {
                ...previous[artist.name],
                enabled: !previous[artist.name].enabled,
            },
        }));
    }, [setArtists])

    useEffect(() => {
        if(Object.keys(artists).length || done) {
            return;
        }
        getArtists()
    }, [getArtists, artists, done]);

    return { artists, loading, refreshArtists, toggleAr };
}

const Artists = () => {
    const { artists, loading, refreshArtists, toggleAr } = useArtists();

    return <div>
        {
            loading ? <Loader /> :
            <div className='container'>
                <button className='btn btn-info px-10 w-100' onClick={refreshArtists}>Refresh from Spotify</button>
                <h4 className="text-muted">Total Artists: {Object.keys(artists).length}</h4>
                {Object.values(artists).map(artist => {
                    return <div key={artist.name} className='artist d-flex'>
                        <div className='d-flex w-100' style={{justifyContent: 'space-between'}}>
                            <div>
                                <h1 className='fw-bold mx-3'>{artist.name}</h1>
                                <h3 className='mx-3 text-muted'>{artist.last_updated}</h3>
                            </div>
                            <button className='btn btn-info m-3 px-4' style={{fontSize: 'xxx-large'}} data-mdb-toggle="button" onClick={() => toggleAr(artist)}>
                                {artist.enabled ? '☑' : '☐'}
                            </button>
                        </div>
                    </div>
                })}
            </div>
        }
    </div>
}

export {Artists};
