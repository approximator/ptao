import React, { Component } from 'react';
import { Button, Table } from 'semantic-ui-react'

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
                <Table.Cell> </Table.Cell>
                <Table.Cell>{`${user.first_name} ${user.last_name}`}</Table.Cell>
                <Table.Cell> </Table.Cell>
                <Table.Cell> </Table.Cell>
                <Table.Cell> </Table.Cell>
            </Table.Row>
        )
        return (
            <div>
                <Table celled padded>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell singleLine></Table.HeaderCell>
                            <Table.HeaderCell></Table.HeaderCell>
                            <Table.HeaderCell></Table.HeaderCell>
                            <Table.HeaderCell></Table.HeaderCell>
                            <Table.HeaderCell></Table.HeaderCell>
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
