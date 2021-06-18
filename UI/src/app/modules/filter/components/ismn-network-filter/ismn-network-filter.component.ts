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

  @Input() filterModel: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;

  networkSelectorVisible: boolean = false;

  networkTree: TreeNode[];

  constructor(public networkService: IsmnNetworkService) {
  }

  ngOnInit(): void {
    this.loadNetworks();
    this.filterModel.subscribe(model => {
      if (model != null) {
        this.loadNetworks();
      }
    });
  }

  showNetworkSelector() {
    this.networkSelectorVisible = true;
  }

  private loadNetworks() {
    this.networkService.getNetworksByDatasetVersionId(this.datasetModel.selectedVersion.id).subscribe(data => {
      this.buildTree(data);
    });
  }

  private buildTree(networks: IsmnNetworkDto[]) {
    let continents: TreeNode[] = [];
    networks.forEach(net => {
      let continentFound = false;
      continents.forEach(continent => {
        if (net.continent == continent.key) {
          continent.children.push(this.networkDtoToTreeModel(net));
          continentFound = true;
        }
      });
      if (continentFound == false) {
        let newContinent: TreeNode = {key: net.continent, label: net.continent};
        newContinent.children = [];
        newContinent.children.push(this.networkDtoToTreeModel(net));
        continents.push(newContinent);
      }
    });
    this.networkTree = continents;
  }

  private networkDtoToTreeModel(network: IsmnNetworkDto): TreeNode<IsmnNetworkDto> {
    let node: TreeNode = {key: network.name, label: network.name, data: network};
    return node;
  }
}
