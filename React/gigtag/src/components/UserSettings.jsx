import { useEffect, useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import { getUserSettings, updateUserCountries } from '../api';
import { Loader } from './Loader';
import { Form, InputGroup } from 'react-bootstrap';
import ReactSelect from 'react-select';
import { TelegramAuth } from './TelegramAuth';

const UserSettings = ({user, setShow, show}) => {
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);
    const [settings, setSettings] = useState({});
    const [countries, setCountries] = useState({"loading": "loading"});

    useEffect(() => {
        if(!show || loading || done) {
            return;
        }

        const getCountries = async () => {
            const res = await fetch("https://restcountries.com/v2/all");
            if (!res.ok) {
                return
            }
            const json = await res.json()

            setCountries(previous => {
                previous = {}
                json.forEach((country) => {
                    previous[country.alpha2Code] = country.name
                });
                return previous;
            });
        }

        const getSettings = async () => {
            setLoading(true);
            if(Object.keys(countries).length === 1) {
                await getCountries();
            }

            const res = await getUserSettings();

            if(!res.ok) {
                console.log("Failed to get user settings", res);
                setLoading(false);
                setDone(true);
                return
            }

            const json = await res.json();
            json.countries = json.countries.split ? json.countries.split(",") : [];
            setSettings(json);

            setDone(true);
            setLoading(false);
        };
        getSettings();
    }, [setLoading, loading, done, show, setSettings, countries])

    const close = () => {
        setShow(false);
        setDone(false);
        setSettings({});
    }

    const onCountrySelect = async (options) => {
        if(!options.length) {
            return;
        }

        await updateUserCountries(options.map(option => option.value).join(","))
    }

    return (    
        <Modal show={show} fullscreen={'xl-down'} onHide={close}>
            <Modal.Header closeButton>
                <Modal.Title>{user.name}</Modal.Title>
            </Modal.Header>
            <Modal.Body className='centered'>
                { loading ? <Loader /> :
                    <div>
                        <InputGroup className='my-1'>
                            <InputGroup.Text id="basic-addon1">@</InputGroup.Text>
                            <Form.Control
                                aria-label="Email"
                                aria-describedby="basic-addon1"
                                defaultValue={settings.email}
                                readOnly
                                disabled
                            />
                        </InputGroup>
                        <InputGroup className='my-1'>
                            <InputGroup.Text id="basic-addon2">ID</InputGroup.Text>
                            <Form.Control
                                aria-label="ID"
                                aria-describedby="basic-addon2"
                                defaultValue={settings.id}
                                readOnly
                                disabled
                            />
                        </InputGroup>
                        <InputGroup className='my-1'>
                            <InputGroup.Text className='w-100' style={{justifyContent: 'center'}} id="basic-addon3">Countries of Interest</InputGroup.Text>
                            <ReactSelect
                                className='w-100 m-1'
                                isMulti
                                isSearchable
                                isClearable
                                closeMenuOnSelect={false}
                                onChange={onCountrySelect}
                                defaultValue={settings.countries?.map(country => {
                                    return {value: country, label: countries[country]}
                                })}
                                options={
                                    Object.keys(countries).map((country) => {
                                        return {value: country, label: countries[country]}
                                    })
                                }
                            />
                        </InputGroup>
                        <TelegramAuth jwtInput={settings.telegramID} />
                    </div>
                }
            </Modal.Body>
        </Modal>
    );
}

export default UserSettings;