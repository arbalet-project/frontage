export const getStatus = ({ response }: { response: any }) => {
    response.status = 200;
    response.body = {
        protocol_version: 3
    }
}