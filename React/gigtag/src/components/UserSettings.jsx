import { useEffect, useState, useCallback } from 'react';
import Modal from 'react-bootstrap/Modal';
import { getUserSettings, updateUserCountries, updateUserNotification } from '../api';
import { Loader } from './Loader';
import { Form, InputGroup } from 'react-bootstrap';
import ReactSelect from 'react-select';
import { TelegramAuth } from './TelegramAuth';
import { countries } from '../countries';

const UserSettings = ({user, setShow, show}) => {
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);
    const [settings, setSettings] = useState({});

    useEffect(() => {
        if(!show || loading || done) {
            return;
        }
        const getSettings = async () => {
            setLoading(true);
            const res = await getUserSettings();

            if(!res.ok) {
                console.log("Failed to get user settings", res);
                setLoading(false);
                setDone(true);
                return
            }

            const json = await res.json();
            json.countries = json.countries?.split ? json.countries.split(",") : [];
            setSettings(json);

            setDone(true);
            setLoading(false);
        };
        getSettings();
    }, [setLoading, loading, done, show, setSettings])

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

    const clearTelegramInfo = useCallback(() => {
        setSettings(settings => {
            settings = {
                ...settings,
                telegramID: "",
            }
            return settings;
        });
    }, [setSettings]);

    const toggleUserNotify = useCallback((e) => {
        updateUserNotification(!settings.notify_for_gigs);

        setSettings(settings => {
            settings = {
                ...settings,
                notify_for_gigs: !settings.notify_for_gigs
            };

            return settings;
        });
    }, [setSettings, settings])

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
                            <InputGroup.Text id="basic-addon2">Notify for New Gigs</InputGroup.Text>
                            <Form.Switch
                                style={{alignSelf: 'center', scale: "1.5", marginLeft: '15px'}}
                                aria-label="notify_new_gigs"
                                aria-describedby="basic-addon2"
                                defaultChecked={settings.notify_for_gigs}
                                onChange={toggleUserNotify}
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
                        <TelegramAuth jwtInput={settings.telegramID} onClear={clearTelegramInfo} />
                    </div>
                }
            </Modal.Body>
        </Modal>
    );
}

export default UserSettings;