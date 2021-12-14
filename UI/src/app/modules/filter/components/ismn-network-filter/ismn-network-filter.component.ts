import {Component, Input, OnInit} from '@angular/core';
import {FilterModel} from '../basic-filter/filter-model';
import {TreeNode} from 'primeng/api';
import {IsmnNetworkService} from '../../../core/services/filter/ismn-network-service';
import {BehaviorSubject} from 'rxjs';
import {DatasetComponentSelectionModel} from '../../../dataset/components/dataset/dataset-component-selection-model';
import {IsmnNetworkDto} from '../../../core/services/filter/ismn-network.dto';


@Component({
  selector: 'qa-ismn-network-filter',
  templateUrl: './ismn-network-filter.component.html',
  styleUrls: ['./ismn-network-filter.component.scss']
})
export class IsmnNetworkFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel$: DatasetComponentSelectionModel;

  networkSelectorVisible = false;

  networkTree: TreeNode[];

  constructor(public networkService: IsmnNetworkService) {
  }

  ngOnInit(): void {
    this.loadNetworks();
    this.filterModel$.subscribe(model => {
      if (model != null) {
        this.loadNetworks();
      }
    });
  }

  showNetworkSelector(): void {
    this.networkSelectorVisible = true;
  }

  private loadNetworks(): void {
    this.networkService.getNetworksByDatasetVersionId(this.datasetModel$.selectedVersion.id).subscribe(data => {
      this.buildTree(data);
    });
  }

  private buildTree(networks: IsmnNetworkDto[]): void {
    const continents: TreeNode[] = [];
    networks.forEach(net => {
      let continentFound = false;
      continents.forEach(continent => {
        if (net.continent === continent.key) {
          continent.children.push(this.networkDtoToTreeModel(net));
          continentFound = true;
        }
      });
      if (continentFound === false) {
        const newContinent: TreeNode = {key: net.continent, label: net.continent};
        newContinent.children = [];
        newContinent.children.push(this.networkDtoToTreeModel(net));
        continents.push(newContinent);
      }
    });
    this.networkTree = continents;
  }

  private networkDtoToTreeModel(network: IsmnNetworkDto): TreeNode<IsmnNetworkDto> {
    return {key: network.name, label: network.name, data: network};
  }

  public onNetworkSelect(e): void {
    if (e.node.data == null) {  // Full continent selected

      e.node.children.forEach(network => {
        console.log('Adding network: ' + network);
        console.log(network);
        this.addNetworkToFilterModel(network);
      });
    } else { // Network selected

    }
    //console.log(e['node']['data']);
    console.log('New paramter: ' + this.filterModel$.value.parameters);
  }

  private addNetworkToFilterModel(network: IsmnNetworkDto): void {
    const filter = this.filterModel$.value;
    if (!filter.parameters.includes(network.name)) {
      if (filter.parameters.length > 0) {
        filter.parameters = filter.parameters + ',';
      }
      filter.parameters = filter.parameters + network.name;
      this.filterModel$.next(filter);
    }
  }

  private removeNetworkFromFilterModel(network: IsmnNetworkDto): void {
    const filter = this.filterModel$.value;
    const posWithComa = filter.parameters.indexOf(',' + network.name);
    const pos = filter.parameters.indexOf(network.name);
    if (posWithComa > -1) {
      filter.parameters.replace(',' + network.name, '');
    } else if (pos > -1) {
      filter.parameters.replace(network.name, '');
    }
  }

}
