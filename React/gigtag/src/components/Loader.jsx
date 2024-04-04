import { Spinner } from "react-bootstrap"

const Loader = ({title}) => {
    return <div className="w-100 text-center m-3">
        <h3>{title}</h3>
        <Spinner className="m-auto" />
        </div>
}

export {Loader};
