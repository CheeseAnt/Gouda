import { useContext } from 'react';
import { UserPlaylists } from 'react-spotify-api'

const SpotifyInfo = () => {
    const [ playlists, setPlaylists ] = useContext({});

    return <UserPlaylists>
        {({data, loadMoreData, loading, error}) => {
                console.log(loading, data, loadMoreData);
                if (data?.items) {
                    setPlaylists(previous => {
                        console.log(previous);
                        data.items.forEach((playlist) => {
                            previous[playlist.id] = playlist.name;
                        })

                        return previous;
                    })
                }
                console.log(playlists);
                return Object.values(playlists).map((name) => <h1>{name}</h1>)
                // return (
                //     playlists?.data?.items?.map(playlist => (
                //         <h1 key={playlist.id}>{playlist.name}</h1>
                //         )
                //     )
                return <h1 key='loadmore' onClick={loadMoreData}>load more</h1>
                // )
            }
        }
    </UserPlaylists>
}

export { SpotifyInfo }
