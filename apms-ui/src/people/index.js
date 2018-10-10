import React, { Component } from 'react';
import { Button, Label, Icon, Table, Rating, Checkbox } from 'semantic-ui-react'
import Moment from 'react-moment';
import UserInfo from './user-info';

class PeoplePage extends Component {

    state = {
        peolpe: []
    }

    constructor(props) {
        super(props)
    }

    componentDidMount() {
        fetch('/api/users')
            .then(res => res.json())
            .then(data => {
                console.log(data);
                this.setState({ peolpe: data['users'] });
            })
    }

    render() {
        const rows = this.state.peolpe.map((user) =>
            <Table.Row key={user.id}>
                <Table.Cell>
                    <Label as='a' style={{ pointerEvents: "auto" }} onClick={() => {
                        let params = new URLSearchParams(this.props.location.search);
                        params.set('owner_id', user.id);
                        params.set('page', 1);
                        this.props.history.push(`/photos?${params.toString()}`);
                    }}><Icon name='user' />
                    </Label>
                </Table.Cell>
                <Table.Cell>{`${user.first_name} ${user.last_name}`}</Table.Cell>
                <Table.Cell>
                    <Rating icon='star' defaultRating={0} maxRating={10} />
                </Table.Cell>
                <Table.Cell>
                    <Moment unix fromNow>
                        {user.date_photos_updated_successfully}
                    </Moment>
                </Table.Cell>
                <Table.Cell>
                    <Checkbox toggle checked={user.pause_update}
                        onChange={() => {
                            // user.pause_update = !user.pause_update
                            console.log(`Use ${user.id} pause_update ${!user.pause_update} -> ${user.pause_update}`)
                        }}
                    />
                </Table.Cell>
            </Table.Row>
        )
        return (
            <div>
                <Table compact celled>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell></Table.HeaderCell>
                            <Table.HeaderCell>Name</Table.HeaderCell>
                            <Table.HeaderCell>Rating</Table.HeaderCell>
                            <Table.HeaderCell>Photos updated</Table.HeaderCell>
                            <Table.HeaderCell>Pause update</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {rows}
                    </Table.Body>
                </Table>
            </div>
        );
    }
}

export default PeoplePage;
